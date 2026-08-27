import re

def clean_pyi(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 依照類別切分，確保我們知道現在在處理哪個類別
    # 這裡假設你的類別定義長這樣 class VecInt: ...
    class_blocks = re.split(r'(\nclass \w+.*?:)', content)
    
    new_content = [class_blocks[0]]  # 檔案頭部的 import
    
    for i in range(1, len(class_blocks), 2):
        class_header = class_blocks[i]   # 例如 "\nclass VecInt:"
        class_body = class_blocks[i+1]   # 該類別內的所有方法
        
        # 針對每個類別內部進行去重
        tokens = re.split(r'(\s*@typing\.overload\s*\n)', class_body)
        new_body = [tokens[0]]
        seen_in_class = set()
        
        for j in range(1, len(tokens), 2):
            separator = tokens[j]
            declaration = tokens[j+1]
            signature = declaration.strip()
            
            if signature not in seen_in_class:
                seen_in_class.add(signature)
                new_body.append(separator)
                new_body.append(declaration)
            else:
                # 只會刪除同一個類別內重複的簽名（例如 VecDouble 裡重複的 __add__）
                print(f"[Removed] Duplicate in {class_header.strip()}: {signature[:50]}")
        
        new_content.append(class_header)
        new_content.append("".join(new_body))

    with open(input_file, 'w', encoding='utf-8') as f:
        f.writelines(new_content)

if __name__ == "__main__":
    clean_pyi('yoVec_pybind_module.pyi')
    print("去重完成！")
    