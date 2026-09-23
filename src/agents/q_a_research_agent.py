import dspy


class GenerateAnswer(dspy.Signature):
    """Answer questions accurately based strictly on the provided context."""

    context: list[str] = dspy.InputField(desc="Relevant text chunks retrieved from vector database")
    question: str = dspy.InputField(desc="The user query")
    answer: str = dspy.OutputField(desc="Clear answer derived strictly from the context")


class RAGAgent(dspy.Module):
    def __init__(self):
        super().__init__()
      
        self.generate_answer = dspy.ChainOfThought(GenerateAnswer)

    
    def forward(self, question: str, retrieved_docs: list[str]) -> dspy.Prediction:
        
        # Step 2: Pass context and question to the DSPy reasoning engine
        prediction = self.generate_answer(context=retrieved_docs, question=question)

        return prediction.answer


    