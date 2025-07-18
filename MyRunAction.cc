#include "G4AnalysisManager.hh"
#include "MyRunAction.hh"

MyRunAction::MyRunAction()
{

  // Define an ntuple
  auto analysisManager = G4AnalysisManager::Instance();

  analysisManager->SetVerboseLevel(1);
  analysisManager->SetDefaultFileType("csv");

  analysisManager->CreateNtuple("MuonSteps", "Step data");
  analysisManager->CreateNtupleIColumn("EventID");
  analysisManager->CreateNtupleIColumn("TrackID");
  analysisManager->CreateNtupleIColumn("StepID");

  analysisManager->CreateNtupleDColumn("x_start");
  analysisManager->CreateNtupleDColumn("y_start");
  analysisManager->CreateNtupleDColumn("z_start");
  analysisManager->CreateNtupleDColumn("t0_start");

  analysisManager->CreateNtupleDColumn("x_end");
  analysisManager->CreateNtupleDColumn("y_end");
  analysisManager->CreateNtupleDColumn("z_end");
  analysisManager->CreateNtupleDColumn("t0_end");

  analysisManager->CreateNtupleDColumn("Edep");
  analysisManager->CreateNtupleDColumn("KineticE");
  analysisManager->CreateNtupleDColumn("StepLength");

  analysisManager->CreateNtupleIColumn("PDG_ID");
  analysisManager->CreateNtupleIColumn("ParentID");
  analysisManager->CreateNtupleSColumn("ProcessName");

  analysisManager->FinishNtuple();
}

void MyRunAction::BeginOfRunAction(const G4Run*)
{
  auto analysisManager = G4AnalysisManager::Instance();
  if (analysisManager->GetFileName().empty()) {
    analysisManager->SetFileName("pgun_mu_steps");
  }
  analysisManager->OpenFile(analysisManager->GetFileName());

}

void MyRunAction::EndOfRunAction(const G4Run*) {
    auto analysisManager = G4AnalysisManager::Instance();
    analysisManager->Write();
    analysisManager->CloseFile();
}
