import { useLexAudit } from './hooks/useLexAudit';
import Header from './components/Header';
import ContractViewer from './components/ContractViewer';
import FindingsPanel from './components/FindingsPanel';
import RulesLibrary from './components/RulesLibrary';
import HistoryPanel from './components/HistoryPanel';
import AddRuleModal from './components/AddRuleModal';

export default function App() {
  const lex = useLexAudit();

  return (
    <div className="app-container">
      <Header
        activeTab={lex.activeTab}
        setActiveTab={lex.setActiveTab}
        rulesCount={lex.rules.length}
        auditsCount={lex.audits.length}
      />

      <main className="main-workspace">
        {lex.activeTab === 'audit' && (
          <>
            <ContractViewer
              isAuditing={lex.isAuditing}
              loadingSteps={lex.loadingSteps}
              selectedAudit={lex.selectedAudit}
              contractParagraphs={lex.contractParagraphs}
              selectedFindingId={lex.selectedFindingId}
              getParagraphViolation={lex.getParagraphViolation}
              onFindingClick={lex.handleFindingClick}
              onFileUpload={lex.handleFileUpload}
            />
            <FindingsPanel
              selectedAudit={lex.selectedAudit}
              filteredFindings={lex.filteredFindings}
              selectedFindingId={lex.selectedFindingId}
              filterSeverity={lex.filterSeverity}
              setFilterSeverity={lex.setFilterSeverity}
              filterStatus={lex.filterStatus}
              setFilterStatus={lex.setFilterStatus}
              onFindingClick={lex.handleFindingClick}
              onApplyCorrection={lex.handleApplyCorrection}
            />
          </>
        )}

        {lex.activeTab === 'rules' && (
          <RulesLibrary
            rules={lex.rules}
            onAddRule={() => lex.setShowAddRuleModal(true)}
            onDeleteRule={lex.handleDeleteRule}
          />
        )}

        {lex.activeTab === 'history' && (
          <HistoryPanel audits={lex.audits} onSelectAudit={lex.handleSelectAudit} />
        )}
      </main>

      {lex.showAddRuleModal && (
        <AddRuleModal
          newRule={lex.newRule}
          setNewRule={lex.setNewRule}
          onSave={lex.handleSaveRule}
          onClose={() => lex.setShowAddRuleModal(false)}
        />
      )}
    </div>
  );
}
