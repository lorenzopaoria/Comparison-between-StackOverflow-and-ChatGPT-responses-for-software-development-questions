# Comparison between StackOverflow and ChatGPT Responses for Software Development Questions

This repository contains a program that compares the responses provided by StackOverflow and ChatGPT for software development-related questions. The goal is to analyze the quality, relevance, and completeness of the responses from these two sources to understand their comparative strengths and weaknesses when it comes to providing helpful information to software developers.

The program includes the following features:

1. **Question Input**: Users can enter a software development-related question to be analyzed.
2. **StackOverflow Response Retrieval**: The program will retrieve the top response from StackOverflow for the given question.
3. **ChatGPT Response Retrieval**: The program will generate a response from ChatGPT for the given question.
4. **Response Comparison**: The program will compare the StackOverflow and ChatGPT responses based on factors such as relevance, completeness, and overall quality.
5. **Analysis Output**: The program will display the results of the comparison, highlighting the strengths and weaknesses of each source.

## Downloading the StackOverflow Dataset

This project utilizes a dataset of software development-related questions and answers from StackOverflow. The dataset was obtained from the following source:

[StackOverflow Data Dump](https://archive.org/details/stackexchange)

Specifically, the dataset used in this project was extracted from the "Posts" table of the StackOverflow data dump. The data contains information such as the question title, body, tags, and the top-voted answer.

To download the dataset, follow these steps:

1. Visit the [StackOverflow Data Dump](https://archive.org/details/stackexchange) page on the Internet Archive.
2. Locate the latest "Posts" table dump for StackOverflow. At the time of writing, the latest available dump is from September 2022.
3. Download the "Posts" table dump in XML.
4. Move the downloaded file to stackOverflowDump folder.
5. Update the file path in the `dataCatalog.py` script to point to the location of the extracted StackOverflow dataset.

## API Limits and Configuration for GPT-4o-mini

This project uses the `gpt-4o-mini` model, with the following rate limits:

| Parameter               | Value                     | Description                                      |
|-------------------------|---------------------------|--------------------------------------------------|
| **RATE_LIMIT_TPM**       | 200,000 tokens/min        | Maximum tokens per minute                        |
| **RATE_LIMIT_BUFFER**    | 5,000 tokens              | Buffer to avoid hitting the rate limit exactly   |
| **TOKEN_COST_PER_REQUEST** | 2,000 tokens (estimated) | Estimated token usage per request               |

These settings help maintain efficient API usage within the rate limits provided by OpenAI. For details, refer to [OpenAI Platform Settings](https://platform.openai.com/settings/organization/limits).

## Usage

To use the program, follow these steps:

1. Clone the repository to your local machine:

   ```
   git clone https://github.com/lorenzopaoria/Comparison-between-StackOverflow-and-ChatGPT-responses-for-software-development-questions.git
   ```

2. Navigate to the cloned repository:

   ```
   cd Comparison-between-StackOverflow-and-ChatGPT-responses-for-software-development-questions
   ```

3. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Navigate to the programs repository:

   ```
   cd py
   ```

5. Run the program:

   ```
   python main.py
   ```

6. Review the analysis results, which will be saved in JSON file for each categories.

## Contributing

If you find any issues or have suggestions for improvements, please feel free to submit a pull request or open an issue in the repository.

## License

This project is licensed under the [MIT License](LICENSE).
