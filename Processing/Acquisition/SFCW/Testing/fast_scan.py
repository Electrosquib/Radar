import numpy as np
import adi

SDR_URI = "usb:"
sdr = adi.ad9361(uri=SDR_URI)


SDR_BW = 20e6
FREQS = [int(i + SDR_BW / 2) for i in np.arange(300e6, 600e6, SDR_BW)]
VERBOSE = True


# Store fastlock profiles for each frequency in the list
fastlock_profiles = []
lo = sdr._ctrl.find_channel("altvoltage0", True)
a = lo.attrs
for count, f in enumerate(FREQS):
    sdr.rx_lo = f
    a["fastlock_store"].value = "0"
    fastlock_profiles.append(a["fastlock_save"].value.split(" ", 1)[1])
    if VERBOSE:
        print(f"[-] Storing Fastlock profiles: {count + 1}/{len(FREQS)} ({(count+1)/len(FREQS)*100:.1f}%)", end="\r")
if VERBOSE:
    print(f"\n[-] Stored {len(fastlock_profiles)} Fastlock profiles.")


# for i in range(8):
#     a["fastlock_load"].value = f"{i} {fastlock_profiles[i]}"

# for i in range(len(fastlock_profiles)):
#     slot = i % 8
#     a["fastlock_recall"].value = str(slot)

#     samples = sdr.rx()

#     next_i = i + 8
#     if next_i < len(fastlock_profiles):
#         a["fastlock_load"].value = f"{slot} {fastlock_profiles[next_i]}"