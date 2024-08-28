import os
import json
import matplotlib.pyplot as plt

# analyze json for count equivalent a
def analyze_a_equivalent(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    equivalent_count = 0
    not_equivalent_count = 0
    
    for item in data:
        if item.get("Are the two answers equivalent?", "No").lower().startswith("yes"):
            equivalent_count += 1
        else:
            not_equivalent_count += 1
    
    return equivalent_count, not_equivalent_count

# create a plot for equivalent and non equivalent a
def plot_results_equivalent(equivalent_count, not_equivalent_count, title, output_file_path):
    labels = ['Equivalent', 'Not Equivalent']
    counts = [equivalent_count, not_equivalent_count]
    colors = ['#008000', '#FF0000']
    
    plt.figure(figsize=(8, 6))
    bars = plt.bar(labels, counts, color=colors)
    plt.xlabel('Answer Comparison')
    plt.ylabel('Number of Questions')
    plt.title(title)
    
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval, int(yval), va='bottom', ha='center') 
    
    plt.savefig(output_file_path)
    plt.close()
    print(f"Comparison plot saved to: {output_file_path}")

# analyze json for count code compilation success and existence present in a
def analyze_a_compilation(data):
    chatgpt_code_compiles = 0
    stackoverflow_code_compiles = 0
    chatgpt_has_code = 0
    stackoverflow_has_code = 0

    for item in data:
        for platform in ["Answer ChatGpt", "Answer StackOverflow"]:
            code_info = item.get("Code and Compile Information", {}).get(platform, {})
            
            # Check if the response has code
            if code_info.get("code") == "Yes":
                if platform == "Answer ChatGpt":
                    chatgpt_has_code += 1
                    # Check if ChatGPT's code compiles
                    if code_info.get("compile", "").lower().startswith("yes"):
                        chatgpt_code_compiles += 1
                elif platform == "Answer StackOverflow":
                    stackoverflow_has_code += 1
                    # Check if StackOverflow's code compiles
                    if code_info.get("compile", "").lower().startswith("yes"):
                        stackoverflow_code_compiles += 1

    return chatgpt_code_compiles, stackoverflow_code_compiles, chatgpt_has_code, stackoverflow_has_code

# create a plot for code compilation success and existence
def plot_results_compilation(results, output_file_path):
    chatgpt_code_compiles, stackoverflow_code_compiles, chatgpt_has_code, stackoverflow_has_code = results

    labels = ['ChatGPT', 'StackOverflow']
    compile_counts = [chatgpt_code_compiles, stackoverflow_code_compiles]
    code_counts = [chatgpt_has_code, stackoverflow_has_code]

    x = range(len(labels)) 
    width = 0.35  

    fig, ax = plt.subplots(figsize=(10, 7))

    color_compile = '#1E90FF' 
    color_code_exists = '#FF6347'  

    bars_compile = ax.bar(
        x, 
        compile_counts, 
        width, 
        label='Code Compiles - Yes', 
        color=color_compile
    )
    
    bars_code_exists = ax.bar(
        [p + width for p in x], 
        code_counts, 
        width, 
        label='Code Exists - Yes', 
        color=color_code_exists
    )

    ax.set_xlabel('Source')
    ax.set_ylabel('Count')
    ax.set_title('Code Compilation and Existence Analysis')
    ax.set_xticks([p + width / 2 for p in x])
    ax.set_xticklabels(labels)
    ax.legend(loc='upper left')

    def add_labels(bars):
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2.0, yval, int(yval), va='bottom', ha='center')

    add_labels(bars_compile)
    add_labels(bars_code_exists)

    plt.tight_layout()
    plt.savefig(output_file_path)
    plt.close()
    print(f"Compilation plot saved to: {output_file_path}")

# write a txt of the analysis results
def write_summary(summary_file_path, equivalent_count= None, not_equivalent_count= None, compilation_results= None):
    with open(summary_file_path, 'w', encoding='utf-8') as f:
        if equivalent_count is not None and not_equivalent_count is not None:
            total = equivalent_count + not_equivalent_count
            f.write(f"Comparison analysis summary:\n")
            f.write(f"Total questions: {total}\n")
            if total > 0:
                f.write(f"Equivalent answers: {equivalent_count} ({(equivalent_count / total) * 100:.2f}%)\n")
                f.write(f"Not equivalent answers: {not_equivalent_count} ({(not_equivalent_count / total) * 100:.2f}%)\n")
            else:
                f.write(f"No data available to calculate percentages.\n")
            f.write("\n")
        
        if compilation_results is not None:
            chatgpt_code_compiles, stackoverflow_code_compiles, chatgpt_has_code, stackoverflow_has_code = compilation_results
            if chatgpt_has_code > 0:
                chatgpt_compile_percentage = (chatgpt_code_compiles / chatgpt_has_code) * 100
            else:
                chatgpt_compile_percentage = 0.0

            if stackoverflow_has_code > 0:
                stackoverflow_compile_percentage = (stackoverflow_code_compiles / stackoverflow_has_code) * 100
            else:
                stackoverflow_compile_percentage = 0.0
            
            f.write(f"Code compilation and existence analysis summary:\n")
            f.write(f"ChatGPT: code exists in {chatgpt_has_code} instances, of which {chatgpt_code_compiles} compile successfully ({chatgpt_compile_percentage:.2f}%).\n")
            f.write(f"StackOverflow: code exists in {stackoverflow_has_code} instances, of which {stackoverflow_code_compiles} compile successfully ({stackoverflow_compile_percentage:.2f}%).\n")
            f.write("\n")
    print(f"Summary file saved to: {summary_file_path}")

# process a json for analyze equivalent or compilarion data
def process_file(file_path, compile= False):
    if not os.path.isfile(file_path):
        return
    
    base_name = os.path.basename(file_path)
    dir_name = os.path.dirname(file_path)


    
    if compile:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        compilation_results = analyze_a_compilation(data)
        plot_results_compilation(compilation_results, os.path.join(dir_name, f"compilation_analysis_{base_name.replace('.json', '.png')}"))
        write_summary(os.path.join(dir_name, f"summary_{base_name.replace('.json', '.txt')}"), compilation_results = compilation_results)
    else:
        equivalent, not_equivalent = analyze_a_equivalent(file_path)
        plot_results_equivalent(equivalent, not_equivalent, f"comparison_analysis_{base_name}", os.path.join(dir_name, f"plot_{base_name.replace('.json', '.png')}"))
        write_summary(os.path.join(dir_name, f"summary_{base_name.replace('.json', '.txt')}"), equivalent_count = equivalent, not_equivalent_count = not_equivalent)

# unisce più json
def merge_json_files(file_paths):
    merged_data = []
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            merged_data.extend(data)
    return merged_data

def main():
    file_paths_equivalent = [
        'q_shorter_than/short_q_openai_answer.json',
        'q_longer_than/long_q_openai_answer.json'
    ]
    
    file_paths_compile = ['qa_with_codes/qa_with_codes_openai_answer.json']

    directory_path_q_tfidf_terms = 'q_for_tfidf_term/'
    if os.path.isdir(directory_path_q_tfidf_terms):
        file_paths_equivalent.extend(
            os.path.join(directory_path_q_tfidf_terms, filename)
            for filename in os.listdir(directory_path_q_tfidf_terms)
            if filename.endswith('.json') and 'openai' in filename
        )
    for file_path in file_paths_equivalent:
        process_file(file_path, compile= False)

    for file_path in file_paths_compile:
        process_file(file_path, compile= True)

    merged_file_paths = file_paths_equivalent
    merged_data = merge_json_files(merged_file_paths)
    merged_file_path = 'merged_equivalent/merged_equivalent_data.json'
    with open(merged_file_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent =4 )
    
    process_file(merged_file_path, compile = False)

if __name__ == "__main__":
    main()