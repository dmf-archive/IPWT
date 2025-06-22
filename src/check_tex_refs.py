import re
import sys
import argparse

def parse_tex_citations(tex_content):
    """从 LaTeX 文件内容中提取所有 \cite{} 命令中的引用标签。"""
    # 正则表达式匹配 \cite{key1, key2, ...} 中的内容
    # 支持 \cite, \citet, \citep 等各种 natbib 命令
    citations = re.findall(r'\\cite[a-zA-Z]*\{([^}]+)\}', tex_content)
    # 将 "key1, key2, key3" 这样的字符串拆分成单个的 key
    citation_keys = set()
    for group in citations:
        keys = [key.strip() for key in group.split(',')]
        citation_keys.update(keys)
    return citation_keys

def parse_bib_keys(bib_content):
    """从 .bib 文件内容中提取所有的文献条目密钥。"""
    # 正则表达式匹配 @article{key, ...} 中的 key
    return set(re.findall(r'@\w+{([^,]+),', bib_content))

def compare_tex_references(tex_path, bib_path):
    """
    比较 LaTeX 手稿和 BibTeX 文件中的引用，生成完整性报告。
    """
    try:
        with open(tex_path, 'r', encoding='utf-8') as f:
            tex_content = f.read()
        tex_citations = parse_tex_citations(tex_content)

        with open(bib_path, 'r', encoding='utf-8') as f:
            bib_content = f.read()
        bib_keys = parse_bib_keys(bib_content)

        missing_citations = tex_citations - bib_keys
        uncited_keys = bib_keys - tex_citations

        print('--- LaTeX 引用与文献库比对报告 ---')
        print(f'手稿 ({tex_path}) 中总引用标签数: {len(tex_citations)}')
        print(f'.bib 文件 ({bib_path}) 中总文献条目数: {len(bib_keys)}')
        print('\\n--- 检查结果 ---')

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
                print(f'\\n【注意】存在于 .bib 文件但手稿中未引用的条目 ({len(uncited_keys)}):')
                for item in sorted(list(uncited_keys)):
                    print(f'  - {item}')
            else:
                print('\\n.bib 文件中的所有文献都在手稿中被引用了。')

    except FileNotFoundError as e:
        print(f"错误: 找不到文件 {e.filename}", file=sys.stderr)
    except Exception as e:
        print(f"发生错误: {e}", file=sys.stderr)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compare citations in a .tex file with a .bib file.')
    parser.add_argument('tex_file', help='Path to the .tex manuscript file.')
    parser.add_argument('bib_file', help='Path to the .bib reference file.')
    args = parser.parse_args()
    
    compare_tex_references(args.tex_file, args.bib_file)
