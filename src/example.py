import time
from ppk2_api.ppk2_api import PPK2_API

ppk2_test = PPK2_API("/dev/ttyACM0", timeout=1, write_timeout=1, exclusive=True)
ppk2_test.get_modifiers()
ppk2_test.set_source_voltage(3300)

ppk2_test.use_source_meter()
ppk2_test.toggle_DUT_power("ON")

ppk2_test.start_measuring()
# measurements are a constant stream of bytes
# the number of measurements in one sampling period depends on the wait between serial reads
# it appears the maximum number of bytes received is 1024
# the sampling rate of the PPK2 is 100 samples per millisecond
idx = 2;
voltages = [3000, 3200, 3300, 3600, 4000, 4200]
ppk2_test.set_source_voltage(voltages[idx])

total = 0
count = 0

while True:
    read_data = ppk2_test.get_data()

    if read_data != b'':
        samples, raw_digital = ppk2_test.get_samples(read_data)
        total += sum(samples)/len(samples)
        count += 1

    if count >= 1000:
        final = total/count
        count = 0
        total = 0

        if final > 1_000_000:
            print(f"{voltages[idx]}: {final/1_000_000:6.2f} A")
        elif final > 1_000:
            print(f"{voltages[idx]}: {final/1_000:6.2f} mA")
        else:
            print(f"{voltages[idx]}: {final:6.2f} uA")

    time.sleep(.001)

ppk2_test.toggle_DUT_power("OFF")
ppk2_test.stop_measuring()
