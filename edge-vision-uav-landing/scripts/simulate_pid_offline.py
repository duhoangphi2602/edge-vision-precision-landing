import csv
import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.control_py.pid_controller import PIDController
from src.evaluation.control_metrics import (
    calculate_overshoot,
    calculate_settling_time,
)


def simulate_scenario(
    init_x: float,
    target_x: float = 0.0,
    total_time: float = 20.0,
    dt: float = 0.05,
) -> dict:
    if dt <= 0.0:
        raise ValueError("dt must be greater than zero")

    if total_time <= 0.0:
        raise ValueError("total_time must be greater than zero")

    pid = PIDController(
        kp=1.2,
        ki=0.0,
        kd=0.1,
        v_max=1.5,
        deadband=0.02,
    )

    current_x = init_x
    steps = int(total_time / dt)

    history_x = []
    samples = []

    for step in range(steps):
        time_s = step * dt

        # Quy ước: error dương khi current_x nằm phía dương của target.
        error_x = current_x - target_x
        vx_cmd = pid.compute(error_x, dt)

        # Mô hình động học 1D lý tưởng, chưa có actuator lag.
        current_x -= vx_cmd * dt

        history_x.append(current_x)
        samples.append({
            "time_s": round(time_s, 4),
            "current_x": current_x,
            "error_x": error_x,
            "vx_cmd": vx_cmd,
        })

    overshoot = calculate_overshoot(history_x, target_x)

    settling_time = calculate_settling_time(
        history_x,
        dt,
        target_x,
        0.05,
    )

    passed = (
        overshoot <= 25.0
        and math.isfinite(settling_time)
        and settling_time <= 5.0
    )

    return {
        "init_x": init_x,
        "final_x": current_x,
        "final_abs_error": abs(current_x - target_x),
        "overshoot_percent": overshoot,
        "settling_time_s": settling_time,
        "status": "PASS" if passed else "FAIL",
        "samples": samples,
    }


def main() -> None:
    scenarios = [0.5, 2.0, -3.0]
    results = [simulate_scenario(init_x) for init_x in scenarios]

    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    summary_path = reports_dir / "pid_simulation_summary.csv"

    with summary_path.open("w", newline="", encoding="utf-8") as file:
        fieldnames = [
            "Init_X",
            "Final_X",
            "FinalAbsError",
            "Overshoot_%",
            "SettlingTime_s",
            "Status",
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            settling_time = result["settling_time_s"]

            writer.writerow({
                "Init_X": result["init_x"],
                "Final_X": round(result["final_x"], 4),
                "FinalAbsError": round(result["final_abs_error"], 4),
                "Overshoot_%": round(result["overshoot_percent"], 2),
                "SettlingTime_s": (
                    round(settling_time, 2)
                    if math.isfinite(settling_time)
                    else "inf"
                ),
                "Status": result["status"],
            })

    print(f"Đã xuất báo cáo: {summary_path}")


if __name__ == "__main__":
    main()