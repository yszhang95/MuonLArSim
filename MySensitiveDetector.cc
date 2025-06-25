#include "MySensitiveDetector.hh"
#include "G4Step.hh"
#include "G4Track.hh"
#include "G4SystemOfUnits.hh"
#include "G4RunManager.hh"

MySensitiveDetector::MySensitiveDetector(const G4String& name)
    : G4VSensitiveDetector(name)
{
    outFile.open("muon_steps.csv");
    outFile << "EventID,TrackID,StepID,x_start(cm),y_start(cm),z_start(cm),t0_start(us),x_end(cm),y_end(cm),z_end(cm),t0_end(us),Edep(MeV),KineticE(MeV),StepLength(cm),PDG_ID,ParentID,ProcessName\n";
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
    G4ThreeVector pos2 = postPoint->GetPosition();

    G4double edep = step->GetTotalEnergyDeposit() / MeV;
    G4double kinE = track->GetKineticEnergy() / MeV;
    G4double stepLength = step->GetStepLength() / cm;

    G4int pdgCode = track->GetDefinition()->GetPDGEncoding();
    G4int parentID = track->GetParentID();

    const G4VProcess* process = prePoint->GetProcessDefinedStep();
    G4String processName = process ? process->GetProcessName() : "none";

    outFile << eventID << "," << trackID << "," << stepID << ","
            << pos.x() / cm << "," << pos.y() / cm << "," << pos.z() / cm << ","
            << std::round(prePoint->GetGlobalTime() / us * 1E5)/1E5 << ","
            << pos2.x() / cm << "," << pos2.y() / cm << "," << pos2.z() / cm << ","
            << std::round(postPoint->GetGlobalTime() / us * 1E5)/1E5 << ","
            << edep << "," << kinE << "," << stepLength << ","
            << pdgCode << "," << parentID << "," << processName << "\n";

    return true;
}
