#include "MySensitiveDetector.hh"
#include "G4Step.hh"
#include "G4Track.hh"
#include "G4SystemOfUnits.hh"
#include "G4RunManager.hh"
#include "G4AnalysisManager.hh"


MySensitiveDetector::MySensitiveDetector(const G4String& name)
    : G4VSensitiveDetector(name)
{
}

MySensitiveDetector::~MySensitiveDetector() {
}

G4bool MySensitiveDetector::ProcessHits(G4Step* step, G4TouchableHistory*) {
    auto event = G4RunManager::GetRunManager()->GetCurrentEvent();
    if (!event) return false;
    auto track = step->GetTrack();

    // if (track->GetDefinition()->GetParticleName() != "mu-" &&
    //    track->GetDefinition()->GetParticleName() != "mu+") return false;

    auto prePoint = step->GetPreStepPoint();
    auto postPoint = step->GetPostStepPoint();

    G4int eventID = G4RunManager::GetRunManager()->GetCurrentEvent()->GetEventID();
    G4int trackID = track->GetTrackID();
    G4int stepID = track->GetCurrentStepNumber();
    G4ThreeVector pos = prePoint->GetPosition();
    G4ThreeVector pos2 = postPoint->GetPosition();

    G4double edep = step->GetTotalEnergyDeposit() / MeV;
    G4double kinE = track->GetKineticEnergy() / MeV;
    G4double stepLength = step->GetStepLength() / cm;

    G4int pdgCode = track->GetDefinition()->GetPDGEncoding();
    G4int parentID = track->GetParentID();

    const G4VProcess* process = prePoint->GetProcessDefinedStep();
    G4String processName = process ? process->GetProcessName() : "none";

    auto t0start = std::round(prePoint->GetGlobalTime() / us * 1E5)/1E5;
    auto t0end = std::round(postPoint->GetGlobalTime() / us * 1E5)/1E5;
    auto analysisManager = G4AnalysisManager::Instance();

    analysisManager->FillNtupleIColumn(0, eventID);
    analysisManager->FillNtupleIColumn(1, trackID);
    analysisManager->FillNtupleIColumn(2, stepID);

    analysisManager->FillNtupleDColumn(3, pos.x() / cm);
    analysisManager->FillNtupleDColumn(4, pos.y() / cm);
    analysisManager->FillNtupleDColumn(5, pos.z() / cm);
    analysisManager->FillNtupleDColumn(6, t0start / us);

    analysisManager->FillNtupleDColumn(7, pos2.x() / cm);
    analysisManager->FillNtupleDColumn(8, pos2.y() / cm);
    analysisManager->FillNtupleDColumn(9, pos2.z() / cm);
    analysisManager->FillNtupleDColumn(10, t0end / us);

    analysisManager->FillNtupleDColumn(11, edep);
    analysisManager->FillNtupleDColumn(12, kinE);
    analysisManager->FillNtupleDColumn(13, stepLength);

    analysisManager->FillNtupleIColumn(14, pdgCode);
    analysisManager->FillNtupleIColumn(15, parentID);
    analysisManager->FillNtupleSColumn(16, processName);

    analysisManager->AddNtupleRow();

    return true;
}
