import sys, time

class SorterHardwareSimulation:
    def __init__(self):
        self.count_plastic = 0
        self.count_metal = 0
        self.count_weighted = 0
        self.max_capacity = 10
        self.stepper_position = 0
        self.servo_angle = 0
        self.lcd_line1 = ""
        self.lcd_line2 = ""

    def read_ultrasonic(self, distance_cm):
        if distance_cm < 70:
            self.servo_angle = 180
            return True
        else:
            self.servo_angle = 0
            return False

    def process_item(self, is_detected, is_metal, weight_grams):
        if not is_detected:
            return "IDLE"

        if is_metal:
            self.stepper_position += 512
            self.count_metal += 1
            item_type = "Metal Can"
        else:
            self.stepper_position -= 512
            self.count_plastic += 1
            item_type = "Plastic Bottle"

        if weight_grams > 10:
            self.count_weighted += 1

        self.update_lcd()
        return item_type

    def update_lcd(self):
        p_str = "FULL" if self.count_plastic >= self.max_capacity else str(self.count_plastic)
        m_str = "FULL" if self.count_metal >= self.max_capacity else str(self.count_metal)
        self.lcd_line1 = f"Plastic : {p_str}"
        self.lcd_line2 = f"Metal   : {m_str}"

def run_tests():
    print("=" * 60)
    print("[TEST SIMULATION] 11_Bottle-Can-Sorter")
    print("=" * 60)

    sim = SorterHardwareSimulation()

    lid_opened = sim.read_ultrasonic(45)
    assert lid_opened is True
    assert sim.servo_angle == 180
    print("1. Ultrasonic Distance Trigger (Lid Servo): OK (Distance: 45cm, Angle: 180 deg)")

    res_plastic = sim.process_item(is_detected=True, is_metal=False, weight_grams=18.5)
    assert res_plastic == "Plastic Bottle"
    assert sim.count_plastic == 1
    assert sim.stepper_position == -512
    print("2. Plastic Bottle Sorting (Inductive + Stepper Left): OK")

    res_metal = sim.process_item(is_detected=True, is_metal=True, weight_grams=14.2)
    assert res_metal == "Metal Can"
    assert sim.count_metal == 1
    assert sim.stepper_position == 0
    print("3. Metal Can Sorting (Proximity + Stepper Right): OK")

    for _ in range(9):
        sim.process_item(is_detected=True, is_metal=False, weight_grams=20.0)

    assert sim.count_plastic == 10
    assert "FULL" in sim.lcd_line1
    print("4. Bin Capacity Overflow & LCD 'FULL' Indicator: OK")
    print("   - LCD Line 1:", sim.lcd_line1)
    print("   - LCD Line 2:", sim.lcd_line2)

    print("Status: TEST PASSED (100% Operational)")

if __name__ == "__main__":
    run_tests()
