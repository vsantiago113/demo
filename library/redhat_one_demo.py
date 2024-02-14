#!/usr/bin/python

# Copyright: (c) 2024, Victor M Santiago <vsantiago113sec@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: redhat_one_demo

short_description: An Ansible module that integrates LangChain with OpenAI LLM, enabling intelligent, automated Q&A within your infrastructure tasks.

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form '2.5.0' and not '2.4'.
version_added: '1.0.0'

description: This Ansible module brings a new level of intelligence to infrastructure automation by combining LangChain with OpenAI or OLLama LLM. Users can ask complex questions within their playbooks and receive context-aware answers, enhancing decision-making and task efficiency. Ideal for DevOps and IT professionals, this module transforms Ansible into a more adaptive and insightful tool for managing and troubleshooting infrastructure.

options:
    model:
        description: Specifies the OpenAI LLM model variant to be used for processing queries. Choose a model based on desired balance between response quality and computation cost.
        required: false
        type: str
    temperature:
        description: Adjusts the creativity and variability of responses from the LLM. Higher values increase creativity at the risk of less predictable outputs. Defaults to a moderate setting for balanced responses.
        required: false
        type: float
    system_message:
        description: Optional system-level message or metadata to provide context or configuration for the LLM's processing. Not required for standard queries.
        required: false
        type: str
    prompt:
        description: The query or command to be processed by the LLM. Should be formulated clearly to yield the most accurate and relevant response.
        required: true
        type: str
    document:
        description: A reference document or text providing additional context or information for the LLM to consider when processing the prompt. Useful for complex queries requiring background knowledge.
        required: true
        type: str

# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
# extends_documentation_fragment:
#     - my_namespace.my_collection.my_doc_fragment_name

author:
    - Your Name (@vsantiago113)
'''

EXAMPLES = r'''
# 
- name: Network Troubleshooting Assistant
  vsantiago113.langchain_ops.redhat_one_demo:
    model: gpt-4
    temperature: 0.2
    system_message: >
        As an expert network architect, your role is pivotal in guiding the engineering team through 
        complex design challenges and resolving technical issues with precision. It is imperative 
        that you rigorously review your solutions before finalizing them to avoid any potential errors. 
        In the event of a misconfiguration, it's crucial to rectify and remove it promptly from the 
        device, as leaving such errors unaddressed can lead to significant operational issues. 
        Your expertise and attention to detail are key in maintaining the integrity and efficiency of 
        the network infrastructure.
    prompt: >
        Review the CLI command outputs from network devices at a specific store to pinpoint any irregularities or issues.Your analysis should be succinct, focusing on critical findings that directly impact network functionality or security.

        Output Format:

        Issues Identified: List the primary issues detected, using brief descriptions. Avoid technical jargon where possible, aiming for clarity.

        Suggestions to Fix: Provide straightforward recommendations for each identified issue. Keep suggestions practical and to the point, suitable for immediate action.

        Possible Commands to Fix Issues: Supply a concise list of CLI commands that could rectify the detected problems. Ensure these commands are precise and applicable.

        Present your findings in the outlined format, prioritizing urgent matters. The aim is to equip the network team with clear, direct, and actionable information for updating the ticket and resolving the issues efficiently.
    document: commands_output.txt
  register: ai

- name: Print AI response
  ansible.builtin.debug:
    msg: "{{ ai['response'] }}"
'''

RETURN = r'''
# Example of possible return value.
message:
    description: The output message that the redhat_one_demo module generates.
    type: str
    returned: always
    response: "Issues Identified..."
'''

from ansible.module_utils.basic import AnsibleModule
import sys
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.document_loaders.csv_loader import CSVLoader


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        model=dict(type='str', required=False, default='llama-pro'),
        temperature=dict(type='float', required=False, default=0.7),
        system_message=dict(type='str', required=False),
        prompt=dict(type='str', required=True),
        document=dict(type='str', required=True)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        response=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)

    if module.params['model'] in ['llama2', 'llama-pro']:
        llm = Ollama(model=module.params['model'], temperature=0.0)
        embeddings = OllamaEmbeddings()
    elif module.params['model'] in ['gpt-4', 'gpt-3.5-turbo']:
        llm = ChatOpenAI(model=module.params['model'], temperature=0.0)
        embeddings = OpenAIEmbeddings()
    else:
        sys.exit('Error: Model not found!')

    document = module.params['document']
    if document.lower().endswith('.md'):
        loader = UnstructuredMarkdownLoader(document)
    elif document.lower().endswith('.csv'):
        loader = CSVLoader(file_path=document, csv_args={
        'delimiter': ',',
        'quotechar': '"'
    })
    else:
        loader = TextLoader(document)

    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter()
    documents = text_splitter.split_documents(docs)
    vector = FAISS.from_documents(documents, embeddings)

    prompt = ChatPromptTemplate.from_template(
        '''
{system_message}
                                        
Your task is to utilize the information provided below to answer the question. 
If the context does not contain enough information to formulate a conclusive 
answer, your response should be "I don't know".

<context>
{context}
</context>

Question: {input}
    ''')

    document_chain = create_stuff_documents_chain(llm, prompt)

    retriever = vector.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    response = retrieval_chain.invoke(
            {
                'input': module.params['prompt'],
                'system_message': module.params['system_message']
            }
        )

    result['response'] = response['answer']

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
