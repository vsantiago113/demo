#!/usr/bin/python

# Copyright: (c) 2024, Victor M Santiago <vsantiago113sec@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: llm_ollama

short_description: An Ansible module that integrates LangChain with Ollama LLM, enabling intelligent, automated Q&A within your infrastructure tasks.

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form '2.5.0' and not '2.4'.
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

# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
# extends_documentation_fragment:
#     - my_namespace.my_collection.my_doc_fragment_name

author:
    - Your Name (@vsantiago113)
'''

EXAMPLES = r'''
# 
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
# Example of possible return value.
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
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        model=dict(type='str', required=False, default='llama2'),
        temperature=dict(type='float', required=False, default=0.7),
        system_message=dict(type='str', required=False),
        prompt=dict(type='str', required=True)
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
    llm = Ollama(model=module.params['model'], temperature=module.params['temperature'])  # TODO: Need error handling here
    prompt = ChatPromptTemplate.from_messages([
        ('system', module.params['system_message']),
        ('user', '{input}')
    ])
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    response = chain.invoke({'input': module.params['prompt']})

    result['response'] = response

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
