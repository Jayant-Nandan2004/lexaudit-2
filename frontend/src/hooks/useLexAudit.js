import { useState, useEffect } from 'react';
import * as api from '../api';
import { LOADING_STEPS } from '../constants';
import { roundToDecimal, splitParagraphs } from '../utils';

const initialSteps = LOADING_STEPS.map((s) => ({ ...s, status: 'pending' }));
const emptyRule = { title: '', description: '', category: 'Liability', severity: 'Major' };

// Encapsulates all LexAudit application state and the handlers that mutate it.
export function useLexAudit() {
  const [activeTab, setActiveTab] = useState('audit'); // audit | rules | history
  const [rules, setRules] = useState([]);
  const [audits, setAudits] = useState([]);
  const [selectedAudit, setSelectedAudit] = useState(null);

  // Workspace
  const [contractParagraphs, setContractParagraphs] = useState([]);
  const [selectedFindingId, setSelectedFindingId] = useState(null);

  // Loading wizard
  const [isAuditing, setIsAuditing] = useState(false);
  const [loadingSteps, setLoadingSteps] = useState(initialSteps);

  // Filters
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');

  // Add-rule modal
  const [showAddRuleModal, setShowAddRuleModal] = useState(false);
  const [newRule, setNewRule] = useState(emptyRule);

  useEffect(() => {
    fetchRules();
    fetchAudits();
  }, []);

  async function fetchRules() {
    try {
      setRules(await api.getRules());
    } catch (err) {
      console.error('Error fetching rules:', err);
    }
  }

  async function fetchAudits() {
    try {
      setAudits(await api.getAudits());
    } catch (err) {
      console.error('Error fetching audits:', err);
    }
  }

  // Drive the animated step tracker. Returns a cancel fn that clears the timers.
  function runLoadingWizard() {
    setIsAuditing(true);
    setLoadingSteps((prev) =>
      prev.map((s) => ({ ...s, status: s.id === 1 ? 'active' : 'pending' })),
    );

    const timers = [
      setTimeout(() => setStepStatus(2, 'active'), 2500),
      setTimeout(() => setStepStatus(3, 'active'), 5500),
      setTimeout(() => setStepStatus(4, 'active'), 8500),
      setTimeout(() => setStepStatus(5, 'active'), 11500),
    ];
    return () => timers.forEach(clearTimeout);
  }

  function setStepStatus(id, status) {
    setLoadingSteps((prev) =>
      prev.map((s) => {
        if (s.id < id) return { ...s, status: 'completed' };
        if (s.id === id) return { ...s, status };
        return s;
      }),
    );
  }

  function loadReport(report) {
    setSelectedAudit(report);
    setContractParagraphs(splitParagraphs(report.contract_text));
  }

  async function handleFileUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;

    const cancelWizard = runLoadingWizard();
    try {
      const report = await api.uploadAudit(file);
      cancelWizard();
      setIsAuditing(false);
      loadReport(report);
      fetchAudits();
    } catch (err) {
      cancelWizard();
      setIsAuditing(false);
      console.error('Upload error:', err);
      alert(`Audit failed: ${err.message}`);
    }
  }

  async function handleSelectAudit(auditId) {
    try {
      loadReport(await api.getAudit(auditId));
      setActiveTab('audit');
    } catch (err) {
      console.error('Error loading audit details:', err);
    }
  }

  async function handleSaveRule(e) {
    e.preventDefault();
    try {
      await api.createRule(newRule);
      fetchRules();
      setShowAddRuleModal(false);
      setNewRule(emptyRule);
    } catch (err) {
      alert(err.message);
    }
  }

  async function handleDeleteRule(ruleId) {
    if (!confirm('Are you sure you want to delete this rule?')) return;
    try {
      await api.deleteRule(ruleId);
      fetchRules();
    } catch (err) {
      console.error('Error deleting rule:', err);
    }
  }

  // Replace the violating text inside the contract draft with the suggested fix,
  // mark the finding as passed, and recompute the compliance score locally.
  function handleApplyCorrection(finding) {
    const { matched_text: originalText, correction: correctionText } = finding;
    if (!originalText || !correctionText) return;

    const matchedIdx = contractParagraphs.findIndex((p) => p.includes(originalText));
    if (matchedIdx === -1) {
      alert(
        'Could not find the exact text in the contract pane to replace. The clause may have already been modified.',
      );
      return;
    }

    const updatedParagraphs = [...contractParagraphs];
    updatedParagraphs[matchedIdx] = updatedParagraphs[matchedIdx].replace(
      originalText,
      correctionText,
    );
    setContractParagraphs(updatedParagraphs);

    const updatedFindings = selectedAudit.findings.map((f) =>
      f.id === finding.id
        ? {
            ...f,
            compliant: true,
            correction: '',
            matched_text: correctionText,
            reasoning: 'Correction applied by user. Clause is now compliant.',
          }
        : f,
    );

    const passedCount = updatedFindings.filter((f) => f.compliant).length;
    const newScore = roundToDecimal((passedCount / updatedFindings.length) * 100, 1);

    setSelectedAudit({
      ...selectedAudit,
      compliance_score: newScore,
      findings: updatedFindings,
      contract_text: updatedParagraphs.join('\n\n'),
    });

    alert('Compliance correction successfully applied to contract draft!');
  }

  // Select a finding and scroll its violating paragraph into view.
  function handleFindingClick(finding) {
    setSelectedFindingId(finding.id);
    if (!finding.matched_text) return;

    const idx = contractParagraphs.findIndex((p) => p.includes(finding.matched_text));
    if (idx !== -1) {
      document.getElementById(`p-${idx}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }

  // Find the (non-compliant) finding whose violating text lives in a paragraph.
  function getParagraphViolation(pText) {
    if (!selectedAudit) return null;
    return selectedAudit.findings.find(
      (f) => !f.compliant && f.matched_text && pText.includes(f.matched_text),
    );
  }

  const filteredFindings = selectedAudit
    ? selectedAudit.findings.filter((f) => {
        const matchSeverity = filterSeverity === 'all' || f.rule_severity === filterSeverity;
        let matchStatus = true;
        if (filterStatus === 'Violations') matchStatus = !f.compliant;
        if (filterStatus === 'Passed') matchStatus = f.compliant;
        return matchSeverity && matchStatus;
      })
    : [];

  return {
    // tab state
    activeTab,
    setActiveTab,
    // data
    rules,
    audits,
    selectedAudit,
    contractParagraphs,
    filteredFindings,
    // workspace selection
    selectedFindingId,
    getParagraphViolation,
    // loading
    isAuditing,
    loadingSteps,
    // filters
    filterSeverity,
    setFilterSeverity,
    filterStatus,
    setFilterStatus,
    // modal + form
    showAddRuleModal,
    setShowAddRuleModal,
    newRule,
    setNewRule,
    // handlers
    handleFileUpload,
    handleSelectAudit,
    handleSaveRule,
    handleDeleteRule,
    handleApplyCorrection,
    handleFindingClick,
  };
}
