from collatz_crypto import SecureCollatzCipher
import collections

def verify_distribution():
    print("--- Verifying Distribution (1-10) ---")
    cipher = SecureCollatzCipher()
    
    # Parameters
    iterations = 100000
    counts = collections.defaultdict(int)
    
    print(f"Running {iterations} iterations...")
    
    for _ in range(iterations):
        state = cipher.step()
        # Map large state to 1-10
        val = (state % 10) + 1
        counts[val] += 1
        
    print("\nResults:")
    print(f"{'Number':<10} | {'Count':<10} | {'Percentage':<10}")
    print("-" * 35)
    
    for i in range(1, 11):
        count = counts[i]
        percent = (count / iterations) * 100
        print(f"{i:<10} | {count:<10} | {percent:.2f}%")
        
    # Chi-squared test hint (optional but good for 'correctness')
    expected = iterations / 10
    max_dev = max(abs(counts[i] - expected) for i in range(1, 11))
    print(f"\nExpected per number: {expected}")
    print(f"Max deviation: {max_dev} ({(max_dev/expected)*100:.2f}%)")
    
    if (max_dev / expected) < 0.05: # Allow 5% deviation
        print("CONCLUSION: Distribution looks UNIFORM (PASS)")
    else:
        print("CONCLUSION: Distribution shows bias (FAIL/WARN)")

if __name__ == "__main__":
    verify_distribution()
