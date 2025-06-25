// #include "DetectorConstruction.hh"
// #include "G4Box.hh"
// #include "G4LogicalVolume.hh"
// #include "G4PVPlacement.hh"
// #include "G4NistManager.hh"
// #include "G4ProductionCuts.hh"
// #include "G4SystemOfUnits.hh"
// #include "G4SDManager.hh"
// #include "MySensitiveDetector.hh"
// #include "G4Region.hh"
// #include "G4UserLimits.hh"

// G4VPhysicalVolume* DetectorConstruction::Construct() {
//     G4NistManager* nist = G4NistManager::Instance();
//     G4Material* worldMat = nist->FindOrBuildMaterial("G4_AIR");
//     G4Material* larMat = nist->FindOrBuildMaterial("G4_lAr");

//     // Create the world
//     G4Box* solidWorld = new G4Box("World", 2*m, 2*m, 2*m);
//     G4LogicalVolume* logicWorld = new G4LogicalVolume(solidWorld, worldMat, "World");
//     G4VPhysicalVolume* physWorld = new G4PVPlacement(0, {}, logicWorld, "World", 0, false, 0);

//     // Sensitive detector manager
//     auto sdManager = G4SDManager::GetSDMpointer();

//     // Boundaries (in mm)
//     std::vector<std::array<std::array<G4double, 2>, 3>> boundaries = {
//         {{{ 3.069, 33.34125}, {-62.076, 62.076}, { 2.462, 64.538}}},
//         {{{63.931, 33.65875}, {-62.076, 62.076}, { 2.462, 64.538}}},
//         {{{ 3.069, 33.34125}, {-62.076, 62.076}, {-64.538, -2.462}}},
//         {{{63.931, 33.65875}, {-62.076, 62.076}, {-64.538, -2.462}}},
//         {{{-63.931, -33.65875}, {-62.076, 62.076}, { 2.462, 64.538}}},
//         {{{ -3.069, -33.34125}, {-62.076, 62.076}, { 2.462, 64.538}}},
//         {{{-63.931, -33.65875}, {-62.076, 62.076}, {-64.538, -2.462}}},
//         {{{ -3.069, -33.34125}, {-62.076, 62.076}, {-64.538, -2.462}}}
//     };

//     for (size_t i = 0; i < boundaries.size(); ++i) {
//         const auto& b = boundaries[i];

//         // Compute center and half-size
//         G4double x_center = (b[0][0] + b[0][1]) / 2.0 * mm;
//         G4double y_center = (b[1][0] + b[1][1]) / 2.0 * mm;
//         G4double z_center = (b[2][0] + b[2][1]) / 2.0 * mm;

//         G4double x_half = std::abs(b[0][1] - b[0][0]) / 2.0 * mm;
//         G4double y_half = std::abs(b[1][1] - b[1][0]) / 2.0 * mm;
//         G4double z_half = std::abs(b[2][1] - b[2][0]) / 2.0 * mm;

//         // Create solid volume
//         G4String solidName = "LArVolume_" + std::to_string(i);
//         G4Box* solid = new G4Box(solidName, x_half, y_half, z_half);

//         // Logical volume
//         G4String logicName = "LArLogic_" + std::to_string(i);
//         G4LogicalVolume* logic = new G4LogicalVolume(solid, larMat, logicName);

//         // Placement
//         G4ThreeVector position(x_center, y_center, z_center);
//         G4String physName = "LArPhys_" + std::to_string(i);
//         new G4PVPlacement(0, position, logic, physName, logicWorld, false, i);

//         // Sensitive detector (one shared or one per volume)
//         G4String sdName = "LArSD_" + std::to_string(i);
//         MySensitiveDetector* sd = new MySensitiveDetector(sdName);
//         sdManager->AddNewDetector(sd);
//         logic->SetSensitiveDetector(sd);

//         // Optionally add region and user limits
//         G4Region* region = new G4Region("LArRegion_" + std::to_string(i));
//         logic->SetRegion(region);
//         region->AddRootLogicalVolume(logic);

//         logic->SetUserLimits(new G4UserLimits(5 * mm));

//         G4ProductionCuts* cuts = new G4ProductionCuts();
//         cuts->SetProductionCut(0.1 * mm);  // Set a cut value, e.g., 1 mm
//         region->SetProductionCuts(cuts);
//     }

//     return physWorld;
// }


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
    G4double maxStep = 2 * mm;

    // Assign user limits to the region
    // larRegion->SetUserLimits(new G4UserLimits(maxStep));
    logicTarget->SetUserLimits(new G4UserLimits(maxStep));


    return physWorld;
}
