#ifndef MY_SENSITIVE_DETECTOR_HH
#define MY_SENSITIVE_DETECTOR_HH

#include "G4VSensitiveDetector.hh"

class G4Step;
class G4TouchableHistory;

class MySensitiveDetector : public G4VSensitiveDetector {
public:
    MySensitiveDetector(const G4String& name);
    virtual ~MySensitiveDetector();

    virtual G4bool ProcessHits(G4Step*, G4TouchableHistory*) override;

};

#endif
