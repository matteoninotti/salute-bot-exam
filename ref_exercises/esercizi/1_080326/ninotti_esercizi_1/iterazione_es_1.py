'''
Autore: Matteo Ninotti
Data: 08/03/2026
Titolo: Si hanno in input due numeri reali A e B e una successione di numeri reali positivi che termina con il valore 0. Si vuole in output la media dei soli numeri compresi tra A e B.
'''

A = 4
B = 7

SEQ = (3, 4.2, -6, 5, 6.7, 10, 7, 0)

def main():
    nums = find_nums()
    avg = calc_avg(nums)
    write_result(avg)

def find_nums():
    nums = []
    for n in SEQ:
        if n >= A and n <= B:
            nums.append(n)
    return nums

def calc_avg(nums):
    somma = 0
    for i in nums:
        somma += i
    avg = round((somma/len(nums)), 4)
    return avg

def write_result(avg):
    print(f"la media dei numeri della sequenza {SEQ} compresi tra {A} e {B} é: ")
    print(avg)

if __name__ == "__main__":
    main()
