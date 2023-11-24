import ReComMaup
import ReComNoMaup

if __name__ == "__main__":
    STATES = ["AZ", "LA", "NV"]

    state = STATES[0]

    if state == "AZ":
        ReComNoMaup.start()
    elif state == "LA":
        ReComNoMaup.start()
    elif state == "NV":
        ReComMaup.start()

    pass
