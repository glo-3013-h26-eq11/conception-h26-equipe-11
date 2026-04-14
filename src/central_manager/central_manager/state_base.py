from typing import Optional


class RoverState:
    def on_enter(self, blackboard: dict) -> None:
        raise NotImplementedError

    def step(self, blackboard: dict) -> Optional[str]:
        raise NotImplementedError

    def execute(self, blackboard: dict) -> Optional[str]:
        return self.step(blackboard)
