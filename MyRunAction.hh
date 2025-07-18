#include "G4UserRunAction.hh"

class MyRunAction : public G4UserRunAction {
public:
    MyRunAction();
    void BeginOfRunAction(const G4Run*) override;
    void EndOfRunAction(const G4Run*) override;
};
