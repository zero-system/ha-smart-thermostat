"""PID controller for pellet stove power level control."""
from datetime import datetime
from simple_pid import PID


class PelletStovePIDController:
    """PID controller specifically tuned for pellet stove control."""

    def __init__(self, kp: float, ki: float, kd: float) -> None:
        """Initialize the PID controller.

        Args:
            kp: Proportional gain
            ki: Integral gain
            kd: Derivative gain
        """
        self._pid = PID(
            Kp=kp,
            Ki=ki,
            Kd=kd,
            setpoint=0,
            output_limits=(1, 5),  # Pellet stove levels 1-5
            sample_time=60,  # Update every 60 seconds
            auto_mode=True,
        )
        self._last_compute = datetime.now()

    def compute(self, current_temp: float, target_temp: float) -> float:
        """Compute the output power level based on current and target temperatures.

        Args:
            current_temp: Current temperature reading
            target_temp: Target temperature setpoint

        Returns:
            float: Recommended power level (1-5)
        """
        # Update setpoint if changed
        if self._pid.setpoint != target_temp:
            self._pid.setpoint = target_temp

        # Calculate time since last compute
        now = datetime.now()
        dt = (now - self._last_compute).total_seconds()
        self._last_compute = now

        # Only update if enough time has passed
        if dt >= self._pid.sample_time:
            return self._pid(current_temp)
        return self._pid._last_output

    def reset(self) -> None:
        """Reset the controller."""