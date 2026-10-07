from fasta_toolkit import Seq, FastaReader
path=input('введите путь к файлу: ')
prot_data=FastaReader(path)
for seq in prot_data.read_records():
    print(seq)
    print(f'Length:{len(seq)}')
    print(f'type:{seq.alphabet()}')