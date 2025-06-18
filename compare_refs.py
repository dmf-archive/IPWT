import re
import sys

def compare_references(manuscript_path, bib_path):
    try:
        with open(manuscript_path, 'r', encoding='utf-8') as f:
            manuscript_content = f.read()
        manuscript_citations = set(re.findall(r'@([a-zA-Z0-9-]+)', manuscript_content))

        with open(bib_path, 'r', encoding='utf-8') as f:
            bib_content = f.read()
        bib_keys = set(re.findall(r'@\w+{([^,]+),', bib_content))

        missing_citations = manuscript_citations - bib_keys
        uncited_keys = bib_keys - manuscript_citations

        print('--- 引用与文献库比对报告 ---')
        print(f'手稿中总引用条目数: {len(manuscript_citations)}')
        print(f'.bib 文件中总文献条目数: {len(bib_keys)}')
        print('\n--- 检查结果 ---')

        if not missing_citations and not uncited_keys:
            print('状态: 完美！所有引用均匹配，无冗余文献。')
        else:
            if missing_citations:
                print(f'【警告】手稿中引用但 .bib 文件缺失的条目 ({len(missing_citations)}):')
                for item in sorted(list(missing_citations)):
                    print(f'  - {item}')
            else:
                print('手稿中的所有引用都在 .bib 文件中找到了。')

            if uncited_keys:
                print(f'\n【注意】存在于 .bib 文件但手稿中未引用的条目 ({len(uncited_keys)}):')
                for item in sorted(list(uncited_keys)):
                    print(f'  - {item}')
            else:
                print('\n.bib 文件中的所有文献都在手稿中被引用了。')

    except FileNotFoundError as e:
        print(f"错误: 找不到文件 {e.filename}", file=sys.stderr)
    except Exception as e:
        print(f"发生错误: {e}", file=sys.stderr)

if __name__ == '__main__':
    compare_references('manuscript.md', 'ref.bib')
