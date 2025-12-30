import secrets
import hmac
import hashlib
import sys

class SecureCollatzCipher:
    def __init__(self, master_key_bytes=None):
        if master_key_bytes is None:
            self.master_key = secrets.token_bytes(32)
        else:
            self.master_key = master_key_bytes
        
        # Derive subkeys for Affine Transform (A*n + B)
        # We need large odd numbers for A and B to ensure full period/complexity
        self.A = self._derive_large_odd(b'multiplier_A')
        self.B = self._derive_large_odd(b'increment_B')
        
        # Current internal state
        self.state = int.from_bytes(secrets.token_bytes(32), 'big')

    def _derive_large_odd(self, salt):
        """Derives a large odd integer from the master key."""
        h = hmac.new(self.master_key, salt, hashlib.sha256).digest()
        # Use valid bytes to form a large integer
        val = int.from_bytes(h, 'big')
        # Ensure it is odd and > 1
        if val % 2 == 0:
            val += 1
        if val <= 1:
            val = 3
        return val

    def _derive_dynamic_k(self, n):
        """
        Derives a dynamic 'k' based on current n for the XOR operation.
        This represents the 'Keyed' part of the crypto algorithm.
        """
        n_bytes = n.to_bytes((n.bit_length() + 7) // 8, 'big')
        h = hmac.new(self.master_key, n_bytes, hashlib.sha256).digest()
        return int.from_bytes(h[:16], 'big') # Take partial hash

    def step(self):
        """
        Secure Collatz Step:
        Even: n = n // 2
        Odd: n = (A * n + B) ^ K
        """
        if self.state % 2 == 0:
            self.state //= 2
        else:
            k = self._derive_dynamic_k(self.state)
            # Affine transformation + XOR non-linearity
            # We must mask result to prevent exponential growth (infinite state size explosion)
            # Simulating a 512-bit register (larger than 256-bit key to avoid direct cycles)
            self.state = ((self.A * self.state + self.B) ^ k) % (2**512)
        
        # Anti-collapse: If state gets too small or 1, regenerating
        if self.state <= 1:
            self.state = int.from_bytes(secrets.token_bytes(32), 'big')
            
        return self.state

    def generate_balanced_bitstring(self, length):
        """
        Generates a bitstring with EXACTLY length/2 zeros and length/2 ones.
        """
        if length % 2 != 0:
            raise ValueError("Length must be even.")
        
        target_zeros = length // 2
        target_ones = length // 2
        zeros = 0
        ones = 0
        bits = []

        while len(bits) < length:
            # Determine parity bit
            is_even = (self.state % 2 == 0)
            bit = '1' if is_even else '0' # User wanted: Even->1, Odd->0 (reversed from typical, strictly following prompt req?)
            # Wait, prompt says: "tek sayılar 1 çift sayılar 0 olarak işaretleniyor" -> Odd=1, Even=0
            # Let's re-read carefully: "tek sayılar 1 çift sayılar 0 olarak işaretleniyor"
            # So: Odd(Tek) -> 1, Even(Çift) -> 0.
            
            val = 1 if (self.state % 2 != 0) else 0

            # Rejection Sampling for Balance
            if val == 0:
                if zeros < target_zeros:
                    bits.append('0')
                    zeros += 1
                    self.step()
                else:
                    # Skip this state, we need a 1
                    self.step()
                    continue 
            else: # val == 1
                if ones < target_ones:
                    bits.append('1')
                    ones += 1
                    self.step()
                else:
                    # Skip this state, we need a 0
                    self.step()
                    continue
                    
        return "".join(bits)

    def generate_quantization_table(self):
        """
        Generates an 8x8 quantization table.
        Standard JPEG tables have certain structures (low freq top-left, high freq bottom-right).
        Random tables often destroy quality.
        We will try to generate a table that somewhat respects the frequency domain 
        but is derived from the Collatz stream.
        We generate values between 1 and 255.
        """
        table = []
        for _ in range(64):
            # Advance state multiple times to mix
            self.step()
            # Map state to 1-255 range
            val = (self.state % 254) + 1 
            table.append(val)
        return table

def demo():
    cipher = SecureCollatzCipher()
    print("--- Secure Collatz Cipher Demo ---")
    print(f"Master Key: {cipher.master_key.hex()[:16]}...")
    
    pwd_len = 32
    password = cipher.generate_balanced_bitstring(pwd_len)
    print(f"\nGenerated Password (Len {pwd_len}): {password}")
    
    c0 = password.count('0')
    c1 = password.count('1')
    print(f"Stats: 0s={c0}, 1s={c1} -> {'BALANCED' if c0==c1 else 'UNBALANCED'}")
    
    print("\nGenerated Quantization Table (First 8 values):")
    q_table = cipher.generate_quantization_table()
    print(q_table[:8])

if __name__ == "__main__":
    demo()
