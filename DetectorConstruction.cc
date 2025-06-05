#include "DetectorConstruction.hh"
#include "G4Box.hh"
#include "G4LogicalVolume.hh"
#include "G4PVPlacement.hh"
#include "G4NistManager.hh"
#include "G4SystemOfUnits.hh"
#include "G4SDManager.hh"
#include "MySensitiveDetector.hh"
#include "G4Region.hh"
#include "G4UserLimits.hh"


G4VPhysicalVolume* DetectorConstruction::Construct() {
    G4NistManager* nist = G4NistManager::Instance();

    G4Material* worldMat = nist->FindOrBuildMaterial("G4_AIR");
    G4Material* larMat = nist->FindOrBuildMaterial("G4_lAr");

    // World
    G4Box* solidWorld = new G4Box("World", 2*m, 2*m, 2*m);
    G4LogicalVolume* logicWorld = new G4LogicalVolume(solidWorld, worldMat, "World");
    G4VPhysicalVolume* physWorld = new G4PVPlacement(0, {}, logicWorld, "World", 0, false, 0);

    // LAr volume
    G4Box* solidTarget = new G4Box("LArVolume", 1*m, 1*m, 1*m);
    G4LogicalVolume* logicTarget = new G4LogicalVolume(solidTarget, larMat, "LArVolume");
    new G4PVPlacement(0, {}, logicTarget, "LArVolume", logicWorld, false, 0);

    // After creating logicTarget:
    auto sdManager = G4SDManager::GetSDMpointer();
    auto larSD = new MySensitiveDetector("LArSD");
    sdManager->AddNewDetector(larSD);
    logicTarget->SetSensitiveDetector(larSD);

    // Create a region for the LAr volume
    G4Region* larRegion = new G4Region("LArRegion");

    // Attach the region to the logical volume
    logicTarget->SetRegion(larRegion);
    larRegion->AddRootLogicalVolume(logicTarget);

    // Define a max step length (e.g., 5 mm)
    G4double maxStep = 5 * mm;

    // Assign user limits to the region
    // larRegion->SetUserLimits(new G4UserLimits(maxStep));
    logicTarget->SetUserLimits(new G4UserLimits(maxStep));


    return physWorld;
}
