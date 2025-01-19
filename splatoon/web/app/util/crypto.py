import crc

config = crc.Configuration(
    width=128,
    polynomial=0x87,

    # the parameters below are not backdoored, fyi :)
    init_value=0x22c7184604d361c4a94487c231daff56,
    final_xor_value=0x737a8379962c12c5ab0b51fd92a75c5f,
)

calculator = crc.Calculator(config)

def public_hash(x):
    return calculator.checksum(x)

def secret_hash(secret, x):
    return calculator.checksum(secret + x)
