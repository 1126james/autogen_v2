def data_dict_summarizer_prompt():
    return """<Data_Dictionary_Analytics_Suggester>
    
    <purpose>
        Analyze the provided data dictionaries thoroughly to identify complex column relationships and propose a diverse set of potential analytics use cases. These use cases should leverage identified relationships to generate meaningful, actionable, and impactful business insights that support strategic decision-making and drive operational enhancements.
    </purpose>
    
    <instructions>
        1. Review all provided data dictionaries meticulously to ensure complete coverage of all datasets and columns.
        2. Examine each dataset's columns, including their definitions, data types, constraints, and any descriptive metadata.
        3. Identify and document all meaningful relationships and combinations of columns within the same dataset and across different datasets that can be utilized for in-depth analysis.
        4. Ensure that every dataset and its relevant columns are considered to fully leverage the available data.
        5. Generate a wide range of potential analytics use cases that utilize these column relationships to address various business objectives such as increasing revenue, reducing costs, understanding customer behavior, and improving operational efficiency.
        6. For each suggested use case, provide a comprehensive explanation that includes:
            - The business objectives it addresses.
            - Granular metrics to be optimized, specifying exact figures, rates, and performance indicators.
            - Specific outcomes expected, detailing measurable and tangible results.
            - Strategic alignment with broader business goals, ensuring contribution to the organization's long-term vision and priorities.
            - Actionable insights to be derived, outlining clear and implementable recommendations.
            - How data relationships inform decision-making processes, explaining the interplay between different data elements.
        7. Ensure that all proposed use cases are actionable, relevant, and solely based on the information provided in the data dictionaries without incorporating any external knowledge or assumptions.
        8. Summarize key relationships between datasets that underpin the proposed analytics use cases, highlighting and utilizing cross-dataset relationships where applicable.
    </instructions>
    
    <output_format>

"use_cases": [
  {
    "use_case_id": "C<UniqueNumber>",
    "title": "<Descriptive Title of the Use Case>",
    "description": "<A comprehensive and specific explanation of the analytics use case, including the business objectives it addresses, granular metrics to be optimized, specific outcomes expected, strategic alignment with business goals, actionable insights to be derived, and how data relationships inform decision-making processes.>",
    "data_sources": [
      "Dataset1.csv",
      "Dataset2.csv"
    ],
    "columns_utilized": [
      "Dataset1.csv.ColumnName",
      "Dataset2.csv.ColumnName"
    ],
    "relationships_leveraged": "<Description of how the columns are related (e.g., primary key, foreign key, common attributes) and how these relationships are utilized in the analysis.>"
  }
]
    </output_format>
    
    <rules>
        1. Exact Naming: Use the exact table and column names as specified in the provided data dictionaries.
        2. Relevance: Only suggest analytics use cases that are directly supported by the relationships and data available in the data dictionaries.
        3. Actionable Use Cases: Ensure that each use case is actionable and aligned with common business objectives such as increasing revenue, reducing costs, understanding customer behavior, and improving operational efficiency.
        4. Comprehensive Utilization: Utilize as many datasets and columns as possible, ensuring that no relevant data is left unexplored or unused in the suggested use cases.
        5. Clarity: Provide clear and concise descriptions for each use case, ensuring that the purpose and methodology are easily understandable.
        6. Structured Output: Adhere strictly to the specified JSON output format to maintain consistency and ease of interpretation across all suggested use cases.
        7. No Assumptions: Base all suggestions solely on the provided data dictionaries without introducing external information or making assumptions beyond the given data.
        8. Unique Identification: Assign a unique ID to each use case to facilitate easy reference and tracking.
        9. Avoid Redundancy: Ensure that each use case is unique and does not duplicate the purpose or methodology of another use case.
        10. Cross-Dataset Relationships: Seek and leverage relationships across different datasets to create comprehensive and insightful use cases that span multiple areas of the business.
        11. Omit Ambiguity: Avoid wording that implies uncertainty, such as "Maybe", "Perhaps", etc.
    </rules>
    
</Data_Dictionary_Analytics_Suggester>"""
