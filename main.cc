#include "G4RunManager.hh"
#include "G4UImanager.hh"
#include "G4VisExecutive.hh"
#include "G4UIExecutive.hh"
#include "G4AnalysisManager.hh"

#include "DetectorConstruction.hh"
#include "PrimaryGeneratorAction.hh"
#include "MyPhysicsList.hh"
#include "MyRunAction.hh"

int main(int argc, char** argv) {
    auto runManager = new G4RunManager();

    runManager->SetUserInitialization(new DetectorConstruction());
    runManager->SetUserInitialization(new MyPhysicsList());
    // runManager->SetUserInitialization(new QGSP_BERT());
    runManager->SetUserAction(new MyRunAction());
    runManager->SetUserAction(new PrimaryGeneratorAction());
    runManager->Initialize();

    G4UImanager* UImanager = G4UImanager::GetUIpointer();
    if (argc == 2) {
        G4AnalysisManager::Instance()->SetDefaultFileType("csv");  // or "root", "xml"

        // Execute macro
        G4String command = "/control/execute ";
        G4String fileName = argv[1];
        UImanager->ApplyCommand(command + fileName);
    } else {
        runManager->BeamOn(50);  // Run 50 events
    }

    delete runManager;
    return 0;
}
