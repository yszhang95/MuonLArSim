#include "MySensitiveDetector.hh"
#include "G4Step.hh"
#include "G4Track.hh"
#include "G4SystemOfUnits.hh"
#include "G4RunManager.hh"

MySensitiveDetector::MySensitiveDetector(const G4String& name)
    : G4VSensitiveDetector(name)
{
    outFile.open("muon_steps.csv");
    outFile << "EventID,TrackID,StepID,x(mm),y(mm),z(mm),Edep(MeV),KineticE(MeV),StepLength(mm),PDG_ID,ParentID,ProcessName\n";
}

MySensitiveDetector::~MySensitiveDetector() {
    if (outFile.is_open()) {
        outFile.close();
    }
}

G4bool MySensitiveDetector::ProcessHits(G4Step* step, G4TouchableHistory*) {
    auto track = step->GetTrack();

    // if (track->GetDefinition()->GetParticleName() != "mu-" &&
    //    track->GetDefinition()->GetParticleName() != "mu+") return false;

    auto prePoint = step->GetPreStepPoint();
    auto postPoint = step->GetPostStepPoint();

    G4int eventID = G4RunManager::GetRunManager()->GetCurrentEvent()->GetEventID();
    G4int trackID = track->GetTrackID();
    G4int stepID = track->GetCurrentStepNumber();
    G4ThreeVector pos = prePoint->GetPosition();

    G4double edep = step->GetTotalEnergyDeposit() / MeV;
    G4double kinE = track->GetKineticEnergy() / MeV;
    G4double stepLength = step->GetStepLength() / mm;

    G4int pdgCode = track->GetDefinition()->GetPDGEncoding();
    G4int parentID = track->GetParentID();

    const G4VProcess* process = prePoint->GetProcessDefinedStep();
    G4String processName = process ? process->GetProcessName() : "none";

    outFile << eventID << "," << trackID << "," << stepID << ","
            << pos.x() / mm << "," << pos.y() / mm << "," << pos.z() / mm << ","
            << edep << "," << kinE << "," << stepLength << ","
            << pdgCode << "," << parentID << "," << processName << "\n";

    return true;
}
