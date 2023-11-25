#from .config.llm_config import fetch_llm_config
from langchain.chat_models import AzureChatOpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from pydantic import BaseModel, Field, conlist
from typing import List
import pandas as pd
import json
import os


llm = AzureChatOpenAI(
                openai_api_type="azure",
                openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
                openai_api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
                deployment_name=os.getenv("AZURE_DEPLOYMENT_ID"),
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                temperature=0.7,
                openai_api_version=os.getenv("AZURE_OPENAI_VERSION")
            )

openai_api_key = os.environ.get("OPENAI_API_KEY")
model = 'gpt-4'
temperature = 0.0

# # importing input text
# with open("input.txt", "r") as f:
#     input = f.read()

# # importing prompt
# with open("prompt.txt", "r") as f:
#     user_prompt = f.read()
input = "pratheesh"
user_prompt = """my name is {input}"""

class FlashCard(BaseModel):
    question: str = Field(description="The question for the flashcard")
    answer: str = Field(description="The answer for the flashcard")
#llm = fetch_llm_config()#ChatOpenAI(openai_api_key=openai_api_key, model=model, temperature=temperature)

pydantic_parser = PydanticOutputParser(pydantic_object=FlashCard)

format_instructions = pydantic_parser.get_format_instructions()

prompt = ChatPromptTemplate.from_template(template=user_prompt)

messages = prompt.format_messages(input_text=input, format_instructions=format_instructions)

output = llm(messages)

flashcards = pydantic_parser.parse(output.content)

print(flashcards)

""" import { z } from "zod";
import { OpenAI } from "langchain/llms/openai";
import { PromptTemplate } from "langchain/prompts";
import {
  StructuredOutputParser,
  OutputFixingParser,
} from "langchain/output_parsers";

import * as dotenv from "dotenv";
dotenv.config();

export const run = async () => {
  const parser = StructuredOutputParser.fromZodSchema(
    z.object({
      name: z.string().describe("Human name"),
      surname: z.string().describe("Human surname"),
      age: z.number().describe("Human age"),
      appearance: z.string().describe("Human appearance description"),
      shortBio: z.string().describe("Short bio secription"),
      university: z.string().optional().describe("University name if attended"),
      gender: z.string().describe("Gender of the human"),
      interests: z
        .array(z.string())
        .describe("json array of strings human interests"),
    })
  );

  const formatInstructions = parser.getFormatInstructions();

  const prompt = new PromptTemplate({
    template:
      "Generate details of a hypothetical person.\n{format_instructions}\nPerson description: {inputText}",
    inputVariables: ["inputText"],
    partialVariables: { format_instructions: formatInstructions },
  });

  const model = new OpenAI({ temperature: 0.5, model: "gpt-3.5-turbo" });

  const input = await prompt.format({
    inputText: "A man, living in Poland.",
  });
  const response = await model.call(input);

  console.log(input);

  console.log(response);

  try {
    console.log(await parser.parse(response));
  } catch (e) {
    console.log("Failed to parse bad output: ", e);

    const fixParser = OutputFixingParser.fromLLM(
      new OpenAI({ temperature: 0, model: "gpt-3.5-turbo" }),
      parser
    );
    const output = await fixParser.parse(response);
    console.log("Fixed output: ", output);
  }
};

run();
 """