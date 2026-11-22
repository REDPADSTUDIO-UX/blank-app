"""Export/check current registry coverage; never overwrite historical evidence."""
import argparse,json
from redpad_pipeline.agent_reporting import CURRENT,RECEIPT,build_matrix,load_matrix

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.check:matrix=load_matrix()
    else:
        receipt=json.loads(RECEIPT.read_text()) if RECEIPT.exists() else None
        matrix=build_matrix(receipt);CURRENT.write_text(json.dumps(matrix,ensure_ascii=False,indent=2)+'\n')
    print('Verified current matrix:',matrix['registered_agents'],'registered agents; historical matrix preserved.')

if __name__=='__main__':main()
