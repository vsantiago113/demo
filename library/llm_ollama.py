#!/usr/bin/python

# Copyright: (c) 2024, Victor M Santiago <vsantiago113sec@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: llm_ollama

short_description: An Ansible module that integrates LangChain with Ollama LLM, enabling intelligent, automated Q&A within your infrastructure tasks.

version_added: '1.0.0'

description: This Ansible module brings a new level of intelligence to infrastructure automation by combining LangChain with Ollama LLM. Users can ask complex questions within their playbooks and receive context-aware answers, enhancing decision-making and task efficiency. Ideal for DevOps and IT professionals, this module transforms Ansible into a more adaptive and insightful tool for managing and troubleshooting infrastructure.

options:
    model:
        description: Specifies the Ollama LLM model variant to be used for processing queries. Choose a model based on desired balance between response quality and computation cost.
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

author:
    - Your Name (@vsantiago113)
'''

EXAMPLES = r'''
- name: VLAN Configuration Assistant
  vsantiago113.langchain_ops.llm_ollama:
    model: llama2
    temperature: 0.3
    system_message: As an expert network architect, you're here to guide engineers through intricate design challenges and effectively resolve issues.
    prompt: Could you provide the commands for configuring VLAN 99 named 'Management' and assigning port fa0/5 to this VLAN, without any explanations?
  register: ai

- name: Print AI response
  ansible.builtin.debug:
    msg: "{{ ai['response'] }}"
'''

RETURN = r'''
message:
    description: The output message that the llm_ollama module generates.
    type: str
    returned: always
    response: "Of course! I'd be happy to help you configure VLAN 99..."
'''

from ansible.module_utils.basic import AnsibleModule
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def run_module():
    module_args = dict(
        model=dict(type='str', required=False, default='llama2'),
        temperature=dict(type='float', required=False, default=0.7),
        system_message=dict(type='str', required=False),
        prompt=dict(type='str', required=True)
    )

    result = dict(
        changed=False,
        response=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    llm = Ollama(model=module.params['model'], temperature=module.params['temperature'])  # TODO: Need error handling here
    prompt = ChatPromptTemplate.from_messages([
        ('system', module.params['system_message']),
        ('user', '{input}')
    ])
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    response = chain.invoke({'input': module.params['prompt']})

    result['response'] = response

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
