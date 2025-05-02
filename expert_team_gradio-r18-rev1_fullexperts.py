import gradio as gr
import ollama
import asyncio
import re

# Define possible team roles with enhanced descriptions
possible_roles = [
    {
        'name': 'Strategic Business Advisor',
        'description': "Analyzes from a business perspective, focusing on strategy, market opportunities, and risks. Ideal for understanding the big-picture implications.",
        'sub_prompt': "Analyze the situation from a high-level business perspective. Focus on strategic implications, market opportunities, and potential risks for a company. Consider long-term goals and competitive advantage when addressing the following:"
    },
    {
        'name': 'Technical Implementation Expert',
        'description': "Focuses on the 'how' - technical aspects, implementation challenges, and infrastructure. Best for understanding the practical execution.",
        'sub_prompt': "Explain the technical aspects and implementation challenges. Focus on the practicalities of execution, potential technical roadblocks, and necessary technologies or infrastructure related to:"
    },
    {
        'name': 'Ethical and Societal Impact Officer',
        'description': "Considers fairness, social responsibility, and broader societal impacts. Important for ensuring responsible and ethical outcomes.",
        'sub_prompt': "Consider the ethical and societal implications. Focus on fairness, social responsibility, potential biases, and the broader impact on society related to:"
    },
    {
        'name': 'Creative Innovation Catalyst',
        'description': "Generates new ideas and unconventional solutions. Great for brainstorming and exploring novel approaches.",
        'sub_prompt': "Think creatively and outside the box. Focus on generating innovative ideas, novel solutions, and unconventional approaches to:"
    },
    {
        'name': 'Clinical Workflow Integration Specialist',
        'description': "Designs and optimizes clinical workflows for LLM integration. Enhances efficiency and reduces bottlenecks in patient care.",
        'sub_prompt': "Design and optimize clinical workflows to seamlessly incorporate LLM tools. Focus on enhancing efficiency, reducing bottlenecks, and improving patient care processes related to:"
    },
    {
        'name': 'Data Governance and Compliance Manager',
        'description': "Establishes data governance policies and ensures regulatory compliance. Focuses on data security and ethical guidelines.",
        'sub_prompt': "Establish and enforce data governance policies and ensure LLM systems comply with healthcare regulations and ethical guidelines. Focus on data security, patient privacy, and legal compliance when considering:"
    },
    {
        'name': 'AI Algorithm Validation and Testing Lead',
        'description': "Develops testing protocols for LLM algorithms. Ensures accuracy, reliability, and safety in clinical applications.",
        'sub_prompt': "Develop robust validation and testing protocols for LLM algorithms. Focus on ensuring accuracy, reliability, safety, and minimizing errors in clinical applications when evaluating:"
    },
    {
        'name': 'Physician-LLM Interface Designer',
        'description': "Creates user-friendly interfaces for physicians interacting with LLM tools. Enhances usability and adoption.",
        'sub_prompt': "Focus on creating intuitive and user-friendly interfaces for physicians interacting with LLM tools. Consider usability, physician adoption, and workflow integration when designing interfaces for:"
    },
    {
        'name': 'Patient Communication and Engagement Strategist',
        'description': "Develops strategies for using LLMs to improve patient communication. Focuses on engagement and understanding of health conditions.",
        'sub_prompt': "Develop strategies for using LLMs to improve patient communication and engagement. Focus on patient understanding, clarity of information, and enhancing the patient experience related to:"
    },
    {
        'name': 'Remote Healthcare and Telemedicine Innovator',
        'description': "Implements LLM solutions for remote patient monitoring and care. Expands healthcare access and delivery.",
        'sub_prompt': "Explore and implement LLM-driven solutions for remote patient monitoring, diagnosis, and care delivery. Focus on expanding healthcare access, improving remote care quality, and technological feasibility for:"
    },
    {
        'name': 'Medical Education and Training Program Developer',
        'description': "Designs training programs for healthcare professionals on LLM use. Focuses on effective and ethical application.",
        'sub_prompt': "Design training programs to educate healthcare professionals on the effective and ethical use of LLM tools in clinical practice. Focus on practical skills, ethical considerations, and responsible AI usage when training on:"
    },
    {
        'name': 'Healthcare Cybersecurity and Data Protection Analyst',
        'description': "Safeguards LLM systems and patient data from cyber threats. Ensures confidentiality and integrity.",
        'sub_prompt': "Specialize in safeguarding LLM systems and patient data from cyber threats. Focus on cybersecurity measures, data protection strategies, and ensuring patient data confidentiality and integrity when implementing:"
    },
    {
        'name': 'Predictive Analytics and Risk Management Specialist',
        'description': "Utilizes LLMs for predictive analytics to identify high-risk patients. Improves preventative care strategies.",
        'sub_prompt': "Utilize LLMs for predictive analytics to identify patients at high risk and improve preventative care strategies. Focus on forecasting, risk identification, and proactive healthcare interventions related to:"
    },
    {
        'name': 'Personalized Medicine and Treatment Optimization Expert',
        'description': "Leverages LLMs for personalized treatment recommendations. Optimizes therapeutic outcomes and minimizes adverse effects.",
        'sub_prompt': "Leverage LLMs to analyze patient data for personalized treatment recommendations. Focus on optimizing therapeutic outcomes, minimizing adverse effects, and tailoring treatments to individual patient needs when considering:"
    },
    {
        'name': 'Medical Imaging and Diagnostic Enhancement Specialist',
        'description': "Applies LLMs to enhance medical image analysis. Improves diagnostic accuracy and speed.",
        'sub_prompt': "Apply LLMs to enhance medical image analysis. Focus on improving diagnostic accuracy, speed, and efficiency in radiology and pathology when using LLMs for:"
    },
    {
        'name': 'Drug Discovery and Development Accelerator',
        'description': "Utilizes LLMs to accelerate drug discovery processes. Optimizes drug development pipelines.",
        'sub_prompt': "Utilize LLMs to accelerate drug discovery processes. Focus on identifying potential drug candidates, optimizing drug development pipelines, and speeding up research timelines related to:"
    },
    {
        'name': 'Public Health and Epidemiology Analyst',
        'description': "Employs LLMs to analyze public health data and track disease outbreaks. Informs public health interventions.",
        'sub_prompt': "Employ LLMs to analyze public health data and track disease outbreaks. Focus on informing public health interventions, policy decisions, and disease prevention strategies based on data insights from:"
    },
    {
        'name': 'Healthcare Cost-Effectiveness and ROI Analyst',
        'description': "Evaluates financial implications of LLM implementation. Focuses on cost savings and ROI.",
        'sub_prompt': "Evaluate the financial implications of LLM implementation. Focus on cost savings, revenue generation, return on investment, and economic viability for healthcare organizations when adopting:"
    },
    {
        'name': 'Legal and Regulatory Compliance Advisor',
        'description': "Provides legal expertise on LLM use in healthcare. Ensures compliance and mitigates legal risks.",
        'sub_prompt': "Provide legal expertise on the regulatory landscape surrounding LLM use in healthcare. Focus on ensuring compliance with laws, mitigating legal risks, and addressing liability concerns related to:"
    },
    {
        'name': 'Patient Advocacy and Rights Officer',
        'description': "Represents patient interests and ensures ethical LLM implementation. Protects patient rights and promotes access.",
        'sub_prompt': "Represent patient interests and ensure LLM systems are implemented ethically and equitably. Focus on protecting patient rights, promoting access, and addressing ethical concerns from a patient advocacy perspective when considering:"
    },
    {
        'name': 'Bias Detection and Mitigation Specialist',
        'description': "Develops methodologies to identify and mitigate biases in LLM algorithms. Ensures fairness and equity.",
        'sub_prompt': "Develop methodologies to identify and mitigate biases in LLM algorithms. Focus on ensuring fairness, equity, and minimizing discriminatory outcomes in healthcare delivery when addressing:"
    },
    {
        'name': 'Explainable AI (XAI) and Transparency Advocate',
        'description': "Promotes transparency and explainability in LLM decision-making. Fosters trust and understanding.",
        'sub_prompt': "Promote transparency and explainability in LLM decision-making. Focus on fostering trust, understanding, and clarity in how LLMs arrive at conclusions in clinical settings when implementing:"
    },
    {
        'name': 'Human-AI Collaboration and Team Dynamics Expert',
        'description': "Optimizes collaboration between healthcare professionals and LLM systems. Enhances team performance.",
        'sub_prompt': "Study and optimize the collaboration between healthcare professionals and LLM systems. Focus on enhancing team performance, improving workflows, and maximizing the synergy between human expertise and AI capabilities in:"
    },
    {
        'name': 'LLM Customization and Fine-tuning Engineer',
        'description': "Customizes and fine-tunes pre-trained LLMs for specific hospital needs. Tailors AI to clinical applications.",
        'sub_prompt': "Specialize in customizing and fine-tuning pre-trained LLMs for specific hospital needs and clinical applications. Focus on performance optimization, adaptation to clinical context, and tailoring AI models for:"
    },
    {
        'name': 'Real-time Clinical Decision Support System Architect',
        'description': "Designs real-time clinical decision support systems powered by LLMs. Aids clinicians at the point of care.",
        'sub_prompt': "Design and implement real-time clinical decision support systems powered by LLMs. Focus on aiding clinicians at the point of care, providing timely insights, and enhancing decision-making in:"
    },
    {
        'name': 'Natural Language Processing (NLP) in Healthcare Specialist',
        'description': "Applies NLP techniques to extract insights from unstructured medical text. Improves data utilization.",
        'sub_prompt': "Focus on applying NLP techniques to extract insights from unstructured medical text. Focus on improving data utilization, clinical understanding, and information retrieval from medical records when analyzing:"
    },
    {
        'name': 'Medical Terminology and Ontology Expert',
        'description': "Ensures accurate use of medical terminology within LLM systems. Enhances data interoperability.",
        'sub_prompt': "Ensure accurate and consistent use of medical terminology and ontologies within LLM systems. Focus on enhancing data interoperability, semantic understanding, and accuracy in medical language processing for:"
    },
    {
        'name': 'Data Integration and Interoperability Engineer',
        'description': "Develops solutions for integrating LLM systems with hospital data infrastructure. Ensures seamless data flow.",
        'sub_prompt': "Develop solutions for integrating LLM systems with existing hospital data infrastructure. Focus on ensuring seamless data flow, interoperability between systems, and efficient data exchange when implementing:"
    },
    {
        'name': 'Scalability and Infrastructure Architect',
        'description': "Designs scalable infrastructure to support LLM deployment across hospital networks. Ensures robust operation.",
        'sub_prompt': "Design scalable and robust infrastructure to support the deployment and operation of LLM systems across large hospital networks. Focus on scalability, reliability, and infrastructure requirements for:"
    },
    {
        'name': 'Continuous Learning and Model Update Strategist',
        'description': "Develops strategies for continuous learning of LLM models. Maintains accuracy and adapts to medical knowledge.",
        'sub_prompt': "Develop strategies for continuous learning and updating of LLM models to maintain accuracy and adapt to evolving medical knowledge. Focus on model improvement, data updates, and long-term performance of LLMs in:"
    },
    {
        'name': 'Emergency and Disaster Response Coordinator (AI-Enhanced)',
        'description': "Utilizes LLMs to enhance hospital emergency response. Optimizes resource allocation during crises.",
        'sub_prompt': "Utilize LLMs to enhance hospital emergency response and optimize resource allocation during crises. Focus on rapid response, efficient resource management, and improved patient care in emergency situations when using LLMs for:"
    },
    {
        'name': 'Medical Literature Review and Synthesis Specialist',
        'description': "Employs LLMs to efficiently review and synthesize medical literature. Keeps clinicians updated.",
        'sub_prompt': "Employ LLMs to efficiently review and synthesize vast amounts of medical literature. Focus on keeping clinicians updated with the latest research, summarizing key findings, and accelerating knowledge dissemination related to:"
    },
    {
        'name': 'Clinical Trial Design and Recruitment Optimizer',
        'description': "Leverages LLMs to optimize clinical trial design and patient recruitment. Accelerates research processes.",
        'sub_prompt': "Leverage LLMs to optimize clinical trial design and identify eligible patients. Focus on accelerating recruitment processes, improving trial efficiency, and enhancing the quality of clinical research related to:"
    },
    {
        'name': 'Quality Improvement and Patient Safety Officer (AI-Driven)',
        'description': "Implements LLM-driven solutions for quality improvement and patient safety. Reduces medical errors.",
        'sub_prompt': "Implement LLM-driven solutions for continuous quality improvement and patient safety monitoring. Focus on reducing medical errors, enhancing care quality, and improving patient outcomes through AI-driven quality assurance in:"
    },
    {
        'name': 'Mental Health and Behavioral Therapy Support Specialist',
        'description': "Explores LLM applications in mental health. Provides AI-driven support for therapy and patient monitoring.",
        'sub_prompt': "Explore LLM applications in mental health, providing AI-driven support for therapy, counseling, and patient monitoring. Focus on improving mental health care access, personalization of therapy, and ethical considerations in AI mental health support for:"
    },
    {
        'name': 'Geriatric and Elder Care Technology Innovator',
        'description': "Develops LLM-based technologies to enhance geriatric care. Improves monitoring of elderly patients.",
        'sub_prompt': "Develop LLM-based technologies to enhance geriatric care and improve monitoring of elderly patients. Focus on addressing age-related health challenges, improving quality of life for seniors, and ethical considerations in AI elder care for:"
    },
    {
        'name': 'Pediatric and Neonatal Care Enhancement Specialist',
        'description': "Focuses on LLM applications in pediatric and neonatal care. Improves diagnosis and treatment of young patients.",
        'sub_prompt': "Focus on LLM applications in pediatric and neonatal care, improving diagnosis, treatment, and monitoring of young patients. Consider the unique needs of pediatric populations, ethical considerations in AI for children's health, and enhancing care quality for:"
    },
    {
        'name': 'Surgical Procedure Planning and Guidance Expert',
        'description': "Utilizes LLMs to assist in surgical planning and provide real-time guidance. Enhances surgical precision.",
        'sub_prompt': "Utilize LLMs to assist in surgical planning and provide real-time guidance during procedures. Focus on enhancing surgical precision, improving planning efficiency, and assisting surgeons with AI-driven insights during:"
    },
    {
        'name': 'Rehabilitation and Physical Therapy Optimization Specialist',
        'description': "Applies LLMs to personalize rehabilitation programs and track patient progress. Optimizes therapy interventions.",
        'sub_prompt': "Apply LLMs to personalize rehabilitation programs and track patient progress. Focus on optimizing physical therapy interventions, tailoring programs to individual needs, and improving rehabilitation outcomes for patients undergoing:"
    },
    {
        'name': 'Medical Device and Equipment Integration Engineer (AI-Enabled)',
        'description': "Integrates LLM capabilities into medical devices and equipment. Enhances functionality and applications.",
        'sub_prompt': "Integrate LLM capabilities into medical devices and equipment, enhancing their functionality and improving diagnostic and therapeutic applications. Focus on technical feasibility, device enhancement, and expanding the capabilities of medical equipment with AI for:"
    },
    {
        'name': 'Airline Pilot (Automation and Safety Expert)',
        'description': "Evaluates LLM integration in flight systems, focusing on automation and safety. Enhances pilot-AI interaction.",
        'sub_prompt': "Evaluate the integration of LLMs in flight systems, focusing on enhancing automation, safety protocols, and pilot-AI interaction in aviation. Consider safety implications, pilot workload, and the role of AI in flight operations when assessing:"
    },
    {
        'name': 'Autonomous Vehicle Engineer (Navigation and Ethics Lead)',
        'description': "Addresses technical and ethical challenges of LLMs in autonomous driving. Focuses on navigation and safety.",
        'sub_prompt': "Address the technical and ethical challenges of LLMs in autonomous driving, focusing on navigation accuracy, decision-making in complex scenarios, and safety. Consider ethical dilemmas, safety regulations, and technological limitations when implementing LLMs in:"
    },
    {
        'name': 'Logistics and Supply Chain Optimization Manager',
        'description': "Optimizes supply chain operations and logistics using LLMs. Enhances efficiency in transportation networks.",
        'sub_prompt': "Utilize LLMs to optimize supply chain operations and enhance logistics. Focus on predicting demand, improving efficiency, reducing costs, and streamlining transportation networks related to:"
    },
    {
        'name': 'Financial Trading Algorithm Developer (Risk and Compliance Focus)',
        'description': "Develops LLM-driven trading algorithms with emphasis on risk management and regulatory compliance.",
        'sub_prompt': "Develop LLM-driven trading algorithms, emphasizing risk management, regulatory compliance, and ethical considerations in financial markets. Focus on algorithm performance, risk mitigation, and adherence to financial regulations when designing:"
    },
    {
        'name': 'Cybersecurity Threat Intelligence Analyst',
        'description': "Employs LLMs to analyze threat patterns and predict cyberattacks. Enhances cybersecurity defenses.",
        'sub_prompt': "Employ LLMs to analyze threat patterns and predict cyberattacks. Focus on enhancing cybersecurity defenses, proactive threat detection, and improving incident response strategies for:"
    },
    {
        'name': 'Educational Content Personalization Specialist',
        'description': "Designs personalized learning experiences using LLMs. Adapts content to individual student needs.",
        'sub_prompt': "Design LLM-powered personalized learning experiences, adapting educational content to individual student needs and learning styles. Focus on student engagement, learning outcomes, and personalized educational pathways when developing:"
    },
    {
        'name': 'Customer Service Chatbot Architect (Empathy and Resolution Focus)',
        'description': "Develops advanced customer service chatbots with LLMs. Focuses on empathy and effective issue resolution.",
        'sub_prompt': "Develop advanced customer service chatbots with LLMs, focusing on improving empathy, personalization, and effective issue resolution. Consider user satisfaction, chatbot efficiency, and natural language understanding capabilities when designing:"
    },
    {
        'name': 'Legal Document Review and Analysis Expert',
        'description': "Automates legal document review and contract analysis using LLMs. Enhances efficiency and accuracy.",
        'sub_prompt': "Utilize LLMs to automate legal document review and contract analysis. Focus on enhancing efficiency, accuracy, and reducing manual workload in legal processes related to:"
    },
    {
        'name': 'Journalism and Content Generation Automation Specialist',
        'description': "Explores LLM use in automating news and content generation. Focuses on fact-checking and accuracy.",
        'sub_prompt': "Explore the use of LLMs in automating news generation and content creation in media and journalism. Focus on fact-checking, accuracy, journalistic integrity, and ethical considerations when automating:"
    },
    {
        'name': 'Entertainment and Creative Content Curator (Personalization Focus)',
        'description': "Personalizes entertainment experiences using LLMs. Curates content recommendations and enhances user engagement.",
        'sub_prompt': "Employ LLMs to personalize entertainment experiences and curate content recommendations. Focus on user engagement, content relevance, and enhancing user satisfaction in entertainment platforms by using LLMs for:"
    },
    {
        'name': 'Agricultural Yield Optimization and Precision Farming Expert',
        'description': "Optimizes agricultural practices using LLMs. Predicts crop yields and promotes sustainable farming.",
        'sub_prompt': "Apply LLMs to optimize agricultural practices and predict crop yields. Focus on resource efficiency, sustainable farming, and improving agricultural productivity through AI-driven insights for:"
    },
    {
        'name': 'Climate Change Modeling and Prediction Analyst',
        'description': "Analyzes climate data and improves climate change models using LLMs. Informs policy decisions.",
        'sub_prompt': "Utilize LLMs to analyze climate data and improve climate change models. Focus on predicting environmental impacts, informing policy decisions, and enhancing climate change understanding through data analysis of:"
    },
    {
        'name': 'Urban Planning and Smart City Designer (AI-Driven)',
        'description': "Incorporates LLMs in urban planning to optimize city infrastructure and resource management.",
        'sub_prompt': "Incorporate LLMs in urban planning to optimize city infrastructure and improve resource management. Focus on enhancing quality of life, sustainable urban development, and efficient city operations in smart cities by using LLMs for:"
    },
    {
        'name': 'Manufacturing Process Optimization Engineer (Predictive Maintenance)',
        'description': "Optimizes manufacturing processes and predicts equipment failures using LLMs. Enhances efficiency.",
        'sub_prompt': "Apply LLMs to optimize manufacturing processes and predict equipment failures. Focus on enhancing efficiency, reducing downtime, and improving predictive maintenance strategies in manufacturing by using LLMs for:"
    },
    {
        'name': 'Energy Grid Management and Smart Distribution Specialist',
        'description': "Optimizes energy distribution and manages smart grids using LLMs. Enhances efficiency of energy networks.",
        'sub_prompt': "Utilize LLMs to optimize energy distribution and manage smart grids. Focus on predicting energy demand, enhancing grid efficiency, and improving energy network management through AI-driven insights for:"
    },
    {
        'name': 'Space Exploration Data Analyst (Anomaly Detection)',
        'description': "Analyzes space exploration data and detects anomalies using LLMs. Accelerates scientific discoveries.",
        'sub_prompt': "Employ LLMs to analyze space exploration data and detect anomalies. Focus on accelerating scientific discoveries, identifying unusual patterns, and enhancing data analysis efficiency in space research related to:"
    },
    {
        'name': 'Robotics and Automation Systems Integrator (LLM-Enhanced)',
        'description': "Integrates LLM capabilities into robotic systems. Enhances autonomy and adaptability.",
        'sub_prompt': "Integrate LLM capabilities into robotic systems, enhancing their autonomy and adaptability. Focus on improving robot performance, enabling natural language interaction, and expanding the applications of robotics in:"
    },
    {
        'name': 'Scientific Research and Hypothesis Generation Assistant',
        'description': "Assists scientists in research and hypothesis generation using LLMs. Accelerates scientific research.",
        'sub_prompt': "Utilize LLMs to assist scientists in literature review and hypothesis generation. Focus on accelerating scientific research, improving research efficiency, and aiding in the formulation of novel hypotheses across disciplines by using LLMs for:"
    },
    {
        'name': 'Supply Chain Risk and Resilience Analyst',
        'description': "Analyzes supply chain vulnerabilities and predicts disruptions using LLMs. Enhances resilience.",
        'sub_prompt': "Employ LLMs to analyze supply chain vulnerabilities and predict disruptions. Focus on enhancing supply chain resilience, mitigating risks, and improving supply chain robustness against unforeseen events by using LLMs for:"
    },
    {
        'name': 'Fraud Detection and Financial Crime Investigator',
        'description': "Detects fraudulent activities and investigates financial crime using LLMs. Enhances efficiency of investigations.",
        'sub_prompt': "Utilize LLMs to detect fraudulent activities and analyze financial transactions. Focus on enhancing the efficiency of financial crime investigations, improving fraud detection accuracy, and reducing financial losses by using LLMs for:"
    },
    {
        'name': 'Human Resources Talent Acquisition and Management Specialist',
        'description': "Optimizes talent acquisition and personalizes employee development using LLMs. Enhances HR processes.",
        'sub_prompt': "Apply LLMs to optimize talent acquisition and personalize employee development. Focus on enhancing HR processes, improving employee engagement, and streamlining talent management within organizations by using LLMs for:"
    },
    {
        'name': 'Political Campaign Strategy and Public Opinion Analyst',
        'description': "Analyzes public opinion and optimizes political campaign strategies using LLMs. Predicts election outcomes.",
        'sub_prompt': "Utilize LLMs to analyze public opinion and optimize political campaign strategies. Focus on predicting election outcomes, understanding voter sentiment, and improving campaign effectiveness by using LLMs for:"
    },
    {
        'name': 'Real Estate Market Trend Analyst and Investment Advisor',
        'description': "Analyzes real estate market trends and provides investment advice using LLMs. Predicts property values.",
        'sub_prompt': "Employ LLMs to analyze real estate market trends and predict property values. Focus on providing data-driven investment advice, understanding market dynamics, and enhancing real estate investment strategies by using LLMs for:"
    },
    {
        'name': 'Art and Music Composition and Generation Assistant',
        'description': "Explores creative potential of LLMs in generating art and music. Pushes boundaries of AI in arts.",
        'sub_prompt': "Explore the creative potential of LLMs in generating art and music. Focus on pushing the boundaries of AI in arts and culture, exploring new creative forms, and assisting artists and musicians in their creative processes by using LLMs for:"
    },
    {
        'name': 'Game Design and Interactive Narrative Developer (AI-Driven)',
        'description': "Creates dynamic game environments and interactive narratives using LLMs. Enhances player experiences.",
        'sub_prompt': "Utilize LLMs to create dynamic game environments and generate interactive narratives. Focus on enhancing player experiences, creating engaging game worlds, and improving game design processes by using LLMs for:"
    },
    {
        'name': 'Personalized Fitness and Wellness Coaching Specialist',
        'description': "Develops personalized fitness and wellness programs using LLMs. Provides customized workout plans.",
        'sub_prompt': "Develop LLM-driven personalized fitness and wellness programs. Focus on providing customized workout plans, nutritional advice, motivational support, and enhancing personal wellness journeys by using LLMs for:"
    },
    {
        'name': 'Language Translation and Cross-cultural Communication Expert',
        'description': "Enhances language translation accuracy and cross-cultural communication using LLMs. Facilitates global interactions.",
        'sub_prompt': "Apply LLMs to enhance language translation accuracy and improve cross-cultural communication. Focus on facilitating global interactions, breaking down language barriers, and improving communication across cultures by using LLMs for:"
    },
    {
        'name': 'Crisis Management and Emergency Response Strategist',
        'description': "Develops strategies for utilizing LLMs in crisis situations. Focuses on rapid information dissemination.",
        'sub_prompt': "Develop strategies for utilizing LLMs in crisis situations. Focus on rapid information dissemination, resource allocation, effective communication, and improving emergency response coordination by using LLMs for:"
    },
    {
        'name': 'Land and Infrastructure Surveyor (AI-Enhanced Mapping and Analysis)',
        'description': "Enhances surveying processes using LLMs. Focuses on AI-driven spatial data analysis and mapping accuracy.",
        'sub_prompt': "Utilize LLMs to enhance surveying processes, focusing on AI-driven analysis of spatial data. Focus on improving mapping accuracy, optimizing infrastructure project planning, and enhancing surveying efficiency by using LLMs for:"
    },
    {
        'name': 'Academic Research Grant Proposal Writer (Efficiency and Impact Focus)',
        'description': "Streamlines grant proposal writing using LLMs. Enhances efficiency and persuasiveness of proposals.",
        'sub_prompt': "Utilize LLMs to streamline the grant proposal writing process. Focus on enhancing efficiency, persuasiveness, alignment with funding priorities, and improving the success rate of academic research grant proposals by using LLMs for:"
    },
    {
        'name': 'University Curriculum Development and Modernization Specialist',
        'description': "Modernizes curriculum design using LLMs. Personalizes learning pathways and enhances student outcomes.",
        'sub_prompt': "Employ LLMs to analyze educational trends and modernize curriculum design. Focus on personalizing learning pathways, enhancing student outcomes, and improving the relevance of university curricula by using LLMs for:"
    },
    {
        'name': 'Student Learning and Performance Analyst (Personalized Feedback)',
        'description': "Analyzes student learning data using LLMs. Provides personalized feedback and improves interventions.",
        'sub_prompt': "Utilize LLMs to analyze student learning data and provide personalized feedback. Focus on identifying at-risk students, improving educational interventions, and enhancing student learning outcomes through data-driven insights from:"
    },
    {
        'name': 'Academic Literature Review and Research Synthesis Expert',
        'description': "Conducts literature reviews and synthesizes research using LLMs. Accelerates academic research.",
        'sub_prompt': "Employ LLMs to efficiently conduct literature reviews and synthesize research findings. Focus on accelerating academic research, improving research efficiency, and enhancing the quality of scholarly work across disciplines by using LLMs for:"
    },
    {
        'name': 'Plagiarism Detection and Academic Integrity Officer (AI-Enhanced)',
        'description': "Enhances plagiarism detection methods using LLMs. Promotes academic integrity in institutions.",
        'sub_prompt': "Utilize LLMs to enhance plagiarism detection methods and promote academic integrity. Focus on ensuring originality in student and faculty work, improving detection accuracy, and upholding ethical standards in academia by using LLMs for:"
    },
    {
        'name': 'Online Course Design and Content Creation Specialist (Interactive Learning)',
        'description': "Develops LLM-powered tools for online course design. Generates interactive content and personalizes learning.",
        'sub_prompt': "Develop LLM-powered tools for designing engaging online courses and generating interactive content. Focus on personalizing the online learning experience, enhancing student engagement, and improving the effectiveness of online education by using LLMs for:"
    },
    {
        'name': 'Language Learning and Tutoring System Developer (Adaptive Learning)',
        'description': "Creates LLM-driven language learning platforms. Provides adaptive tutoring and personalized feedback.",
        'sub_prompt': "Create LLM-driven language learning platforms, providing adaptive tutoring and personalized feedback. Focus on improving language acquisition, tailoring learning experiences to individual needs, and enhancing language learning outcomes by using LLMs for:"
    },
    {
        'name': 'Automated Essay Scoring and Feedback System Architect',
        'description': "Designs automated essay scoring systems using LLMs. Provides efficient feedback to students.",
        'sub_prompt': "Design automated essay scoring systems using LLMs, providing efficient and consistent feedback to students. Focus on reducing instructor workload, improving feedback quality, and enhancing student writing skills through AI-driven essay evaluation for:"
    },
    {
        'name': 'Research Data Management and Curation Specialist (AI-Assisted)',
        'description': "Enhances research data management using LLMs. Automates data curation and improves accessibility.",
        'sub_prompt': "Utilize LLMs to enhance research data management and automate data curation processes. Focus on improving data accessibility, reusability, and efficiency in research data handling by using LLMs for:"
    },
    {
        'name': 'Conference and Workshop Program Organizer (AI-Driven Scheduling)',
        'description': "Optimizes conference scheduling using LLMs. Personalizes attendee experiences and enhances event organization.",
        'sub_prompt': "Employ LLMs to optimize conference and workshop scheduling. Focus on personalizing attendee experiences, enhancing event organization, and improving logistical efficiency in academic events by using LLMs for:"
    },
    {
        'name': 'University Library Resource and Search Optimization Expert',
        'description': "Improves library resource discovery and search functionality using LLMs. Personalizes research support.",
        'sub_prompt': "Utilize LLMs to improve library resource discovery and enhance search functionality. Focus on personalizing research support for students and faculty, improving access to information, and optimizing library services by using LLMs for:"
    },
    {
        'name': 'Academic Writing and Publication Support Specialist (AI-Enhanced Editing)',
        'description': "Provides LLM-powered tools for academic writing. Offers AI-driven editing and publication guidance.",
        'sub_prompt': "Provide LLM-powered tools to support academic writing, offering AI-driven editing and style suggestions. Focus on enhancing writing quality, improving publication success, and assisting academics in scholarly communication by using LLMs for:"
    },
    {
        'name': 'Accessibility and Inclusive Education Technology Developer (LLM-Powered)',
        'description': "Develops LLM-based technologies to enhance accessibility in education. Promotes inclusive learning.",
        'sub_prompt': "Develop LLM-based technologies to enhance accessibility in education, providing tools for students with disabilities and promoting inclusive learning environments. Focus on equitable access to education, personalized support for diverse learners, and improving inclusivity in educational settings by using LLMs for:"
    },
    {
        'name': 'Accident Site Investigation Lead',
        'description': "Oversees physical investigation of accident site. Coordinates evidence collection and wreckage analysis.",
        'sub_prompt': "Oversee the physical investigation of the accident site. Focus on coordinating evidence collection, wreckage analysis, and ensuring thorough site examination to determine accident causes related to:"
    },
    {
        'name': 'Air Traffic Control Procedure Analyst',
        'description': "Examines air traffic control procedures at accident time. Identifies deviations and contributing factors.",
        'sub_prompt': "Examine the air traffic control procedures in place at the time of the accident. Focus on identifying any deviations from standard protocols, procedural flaws, and contributing factors within ATC operations related to:"
    },
    {
        'name': 'Aircraft Systems and Maintenance Expert',
        'description': "Analyzes aircraft systems and maintenance history. Investigates potential equipment malfunctions.",
        'sub_prompt': "Analyze the aircraft's mechanical and electronic systems and maintenance history. Focus on potential equipment malfunctions, system failures, maintenance lapses, and aircraft-related factors contributing to:"
    },
    {
        'name': 'Pilot Performance and Human Factors Specialist',
        'description': "Assesses pilot actions and human factors. Investigates pilot training and experience.",
        'sub_prompt': "Assess the pilot's actions, training, experience, and any human factors that may have contributed to the accident. Focus on pilot performance, decision-making under stress, and human error aspects related to:"
    },
    {
        'name': 'Meteorological Data Analyst',
        'description': "Analyzes weather conditions at accident time. Evaluates impact on flight operations.",
        'sub_prompt': "Analyze weather conditions at the time of the accident and their potential impact on flight operations. Focus on meteorological factors, weather-related hazards, and the influence of environmental conditions on:"
    },
    {
        'name': 'Flight Data Recorder (FDR) and Cockpit Voice Recorder (CVR) Analyst',
        'description': "Leads analysis of FDR and CVR data. Reconstructs flight path and crew actions.",
        'sub_prompt': "Lead the analysis of FDR and CVR data to reconstruct the flight path, crew actions, and communication. Focus on data interpretation, timeline reconstruction, and extracting critical information from flight recorders related to:"
    },
    {
        'name': 'Airspace and Navigation Systems Expert',
        'description': "Evaluates airspace design and navigation aids. Investigates navigation system issues.",
        'sub_prompt': "Evaluate the airspace design and navigation aids. Focus on potential issues with navigation systems, airspace complexity, and navigational factors contributing to:"
    },
    {
        'name': 'Emergency Response and Rescue Operations Evaluator',
        'description': "Assesses effectiveness of emergency response and rescue operations. Evaluates post-accident support.",
        'sub_prompt': "Assess the effectiveness of the emergency response and rescue operations. Focus on response times, coordination efficiency, resource utilization, and post-accident victim support related to:"
    },
    {
        'name': 'Airport Operations and Ground Crew Analyst',
        'description': "Examines airport operations and ground crew procedures. Investigates ground-related factors.",
        'sub_prompt': "Examine airport operations and ground crew procedures. Focus on potential ground-related factors, airport operational issues, and ground crew actions contributing to:"
    },
    {
        'name': 'Witness Interview and Testimony Coordinator',
        'description': "Manages witness interviews and testimony collection. Ensures accurate documentation.",
        'sub_prompt': "Manage the process of interviewing witnesses and collecting testimonies. Focus on ensuring accurate documentation, reliable witness accounts, and gathering comprehensive information from eyewitnesses related to:"
    },
    {
        'name': 'Safety Management Systems (SMS) Auditor',
        'description': "Reviews airline and ATC safety management systems. Evaluates effectiveness and compliance.",
        'sub_prompt': "Review the airline's and air traffic control's safety management systems for effectiveness and compliance. Focus on SMS protocols, safety culture, and adherence to safety management standards within aviation operations related to:"
    },
    {
        'name': 'Regulatory Compliance and Oversight Investigator',
        'description': "Investigates adherence to FAA regulations and oversight procedures. Identifies regulatory gaps.",
        'sub_prompt': "Investigate adherence to FAA regulations and oversight procedures. Focus on regulatory compliance, oversight effectiveness, and identifying potential regulatory gaps or violations related to:"
    },
    {
        'name': 'Air Traffic Controller Performance Analyst',
        'description': "Evaluates air traffic controller performance and workload. Investigates human factors in ATC.",
        'sub_prompt': "Evaluate the performance of air traffic controllers involved, workload, and potential human factors in ATC. Focus on controller actions, workload management, communication effectiveness, and human error aspects in air traffic control during:"
    },
    {
        'name': 'Communication Systems and Protocol Expert',
        'description': "Analyzes communication systems and protocols used during flight. Investigates communication issues.",
        'sub_prompt': "Analyze communication systems, radio frequencies, and communication protocols used during the flight. Focus on communication clarity, protocol adherence, and potential communication breakdowns or misunderstandings during:"
    },
    {
        'name': 'Risk Assessment and Systemic Vulnerability Analyst',
        'description': "Identifies systemic vulnerabilities in air traffic system. Assesses overall risk factors.",
        'sub_prompt': "Identify systemic vulnerabilities in the air traffic system and assess overall risk factors contributing to the accident. Focus on broader system weaknesses, risk management practices, and systemic issues within aviation safety related to:"
    },
    {
        'name': 'Legal and Liability Determination Specialist',
        'description': "Provides legal analysis on liability and regulatory violations. Determines legal actions.",
        'sub_prompt': "Provide legal analysis on liability, regulatory violations, and potential legal actions arising from the accident. Focus on legal responsibilities, liability assessment, and regulatory implications in the aftermath of:"
    },
    {
        'name': 'Victim and Family Support Liaison',
        'description': "Acts as liaison for victims' families. Provides information, support, and resources.",
        'sub_prompt': "Act as a primary point of contact for victims' families, providing information, support, and resources. Focus on victim support, family communication, and addressing the needs of those affected by:"
    },
    {
        'name': 'Public Relations and Media Communication Manager',
        'description': "Manages media relations and public communication. Ensures transparent information dissemination.",
        'sub_prompt': "Manage media relations and public communication, and ensure transparent and accurate information dissemination. Focus on public perception, media messaging, and maintaining transparency in communication about:"
    },
    {
        'name': 'Data Visualization and Accident Reconstruction Modeler',
        'description': "Creates visual models and simulations for accident reconstruction. Aids in understanding contributing factors.",
        'sub_prompt': "Create visual models and simulations to reconstruct the accident sequence and aid in understanding the contributing factors. Focus on data visualization, accident dynamics, and creating a clear reconstruction of events leading to:"
    },
    {
        'name': 'Cybersecurity and System Security Analyst (Aviation Systems)',
        'description': "Assesses cybersecurity aspects of aviation systems. Investigates potential cyber threats.",
        'sub_prompt': "Assess cybersecurity aspects of aviation systems and potential cyber threats and vulnerabilities. Focus on system security, cyber risks, and potential security breaches in aviation technology related to:"
    },
    {
        'name': 'Training and Crew Resource Management (CRM) Expert',
        'description': "Evaluates pilot and ATC training programs and CRM effectiveness. Investigates training aspects.",
        'sub_prompt': "Evaluate pilot and air traffic controller training programs and crew resource management effectiveness. Focus on training quality, CRM protocols, and human performance enhancement in aviation operations related to:"
    },
    {
        'name': 'Air Traffic Management (ATM) Technology Specialist',
        'description': "Analyzes role of ATM technologies and automation. Investigates technology-related issues.",
        'sub_prompt': "Analyze the role of air traffic management technologies and automation and potential technology-related issues. Focus on ATM system performance, automation reliability, and technology-related factors in air traffic control during:"
    },
    {
        'name': 'Airworthiness and Aircraft Certification Expert',
        'description': "Reviews aircraft airworthiness and certification. Investigates compliance with directives.",
        'sub_prompt': "Review the aircraft's airworthiness certificate and design certifications and compliance with airworthiness directives. Focus on aircraft certification standards, airworthiness compliance, and design-related factors contributing to:"
    },
    {
        'name': 'Load and Weight Balance Analyst',
        'description': "Examines aircraft load and weight balance at accident time. Evaluates impact on flight dynamics.",
        'sub_prompt': "Examine the aircraft's load and weight balance at the time of the accident and potential impact on flight dynamics. Focus on weight distribution, load factors, and their influence on aircraft stability and control during:"
    },
    {
        'name': 'Fuel Systems and Engine Performance Analyst',
        'description': "Analyzes fuel systems and engine performance. Investigates engine-related malfunctions.",
        'sub_prompt': "Analyze fuel systems and engine performance and potential engine-related malfunctions. Focus on engine operation, fuel system integrity, and potential engine failures or performance issues contributing to:"
    },
    {
        'name': 'Structural Integrity and Wreckage Analysis Engineer',
        'description': "Leads structural analysis of wreckage. Identifies structural failures or weaknesses.",
        'sub_prompt': "Lead the structural analysis of the aircraft wreckage to identify structural failures or weaknesses. Focus on structural integrity, material fatigue, and identifying any pre-existing structural issues in the aircraft involved in:"
    },
    {
        'name': 'Materials Science and Metallurgy Expert',
        'description': "Conducts materials analysis on wreckage components. Identifies material defects.",
        'sub_prompt': "Conduct materials analysis on wreckage components to identify material fatigue, corrosion, or manufacturing defects. Focus on material properties, metallurgical analysis, and identifying material-related failures in aircraft components from:"
    },
    {
        'name': 'Explosives and Hazardous Materials Specialist (Security Focus)',
        'description': "Investigates potential involvement of explosives or hazardous materials. Focuses on security aspects.",
        'sub_prompt': "Investigate potential involvement of explosives or hazardous materials as a cause or contributing factor. Focus on security protocols, threat assessment, and ruling out or confirming any security-related breaches in:"
    },
    {
        'name': 'Security Protocol and Threat Assessment Expert',
        'description': "Evaluates security protocols and threat assessments. Investigates potential security breaches.",
        'sub_prompt': "Evaluate security protocols and threat assessments and potential security breaches related to the accident. Focus on security vulnerabilities, protocol weaknesses, and potential security-related factors contributing to:"
    },
    {
        'name': 'International Aviation Regulations and Standards Advisor',
        'description': "Provides expertise on international aviation regulations and standards. Addresses cross-border implications.",
        'sub_prompt': "Provide expertise on international aviation regulations and standards and cross-border implications. Focus on international regulatory frameworks, compliance with global standards, and cross-border jurisdictional aspects of:"
    },
    {
        'name': 'Insurance and Financial Risk Assessor (Aviation Industry)',
        'description': "Assesses insurance implications and financial risks in aviation industry. Evaluates economic impact.",
        'sub_prompt': "Assess insurance implications and financial risks and economic impact of the accident on involved parties. Focus on insurance coverage, financial liabilities, and economic consequences for airlines and stakeholders affected by:"
    },
    {
        'name': 'Environmental Impact Assessment Specialist (Accident Site)',
        'description': "Evaluates environmental impact of accident site. Investigates fuel spills and contamination.",
        'sub_prompt': "Evaluate environmental impact of the accident, fuel spills, and contamination at the accident site. Focus on ecological damage, environmental remediation, and assessing the long-term environmental consequences of:"
    },
    {
        'name': 'Community and Stakeholder Liaison',
        'description': "Engages with local communities and stakeholders. Addresses concerns related to accident and investigation.",
        'sub_prompt': "Engage with local communities and stakeholders and address concerns related to the accident and investigation. Focus on community relations, public engagement, and addressing local concerns and impacts resulting from:"
    },
    {
        'name': 'Government and Political Relations Advisor',
        'description': "Advises on government relations and political sensitivities. Manages communication with agencies.",
        'sub_prompt': "Advise on government relations, political sensitivities, and communication with government agencies. Focus on political implications, government interactions, and managing relationships with regulatory bodies in the context of:"
    },
    {
        'name': 'Airline Operational Procedures and Manuals Reviewer',
        'description': "Reviews airline operational procedures and manuals. Evaluates adherence to SOPs.",
        'sub_prompt': "Review airline's operational procedures and manuals and adherence to standard operating procedures (SOPs). Focus on procedural compliance, operational guidelines, and identifying any deviations from standard airline practices in:"
    },
    {
        'name': 'Air Traffic Control Facility and Equipment Inspector',
        'description': "Inspects ATC facilities and equipment. Ensures proper functioning and maintenance.",
        'sub_prompt': "Inspect air traffic control facilities and equipment and ensure proper functioning and maintenance. Focus on equipment reliability, facility infrastructure, and operational readiness of air traffic control systems involved in:"
    },
    {
        'name': 'Independent Safety Board Representative',
        'description': "Serves as independent representative on safety board. Ensures objectivity and impartiality.",
        'sub_prompt': "Serve as an independent representative on the safety board, ensuring objectivity and impartiality in the investigation. Focus on unbiased assessment, independent oversight, and maintaining investigative integrity throughout the inquiry into:"
    },
    {
        'name': 'Accident Investigation Report Writer and Documentation Lead',
        'description': "Leads writing of accident investigation report. Ensures comprehensive documentation and clear findings.",
        'sub_prompt': "Lead the writing of the accident investigation report, ensuring comprehensive documentation and clear findings. Focus on report accuracy, clarity of conclusions, and thorough documentation of investigation processes and findings related to:"
    },
    {
        'name': 'Recommendation and Safety Improvement Strategist',
        'description': "Develops safety recommendations based on findings. Prevents future accidents and improves safety.",
        'sub_prompt': "Develop safety recommendations based on investigation findings to prevent future accidents and improve aviation safety. Focus on actionable recommendations, preventative measures, and enhancing aviation safety protocols based on the analysis of:"
    },
    {
        'name': 'Pilot Union and Air Traffic Controller Association Liaison',
        'description': "Liaises with pilot unions and ATC associations. Gathers input and addresses concerns.",
        'sub_prompt': "Liaise with pilot unions and air traffic controller associations to gather input and address concerns from professional groups. Focus on pilot and controller perspectives, professional insights, and addressing operational concerns raised by aviation professionals regarding:"
    }
]

# Temperature Presets - descriptive names
temperature_presets = {
    "Cautious": 0.3, # Best for factual or sensitive topics
    "Balanced": 0.7, # Good for general use, moderate creativity
    "Creative": 0.9, # Ideal for brainstorming and idea generation
}

# Reorganized Model Options for Clarity and Readability
available_models = ['qwen:0.5b', 'smollm2:135m', 'gemma2:2b','llava:7b','dolphin-llama3:latest']
model_options = {model: model for model in available_models} # Using dict comprehension for clarity

evaluation_models = ['gemma2:2b', 'dolphin-llama3:latest'] # Limiting evaluation models for focused selection
evaluation_model_options = {model: model for model in evaluation_models}


# --- Utility Functions (Improved Structure) ---
async def generate_expert_response(question, role, model_name, temperature_setting):
    """
    Generates a response from a specified expert role using a given model and temperature.
    Handles potential errors and provides informative error messages.
    """
    temperature = temperature_presets.get(temperature_setting, 0.7) # Default to 'Balanced' if not found
    prompt = f"You are a {role['name']}. {role['sub_prompt']} {question}"
    try:
        ollama.temperature = temperature
        response = await asyncio.to_thread(ollama.chat, model=model_name, messages=[{'role': 'user', 'content': prompt}])
        print (response)
        return response['message']['content']
  
    except Exception as e:
        error_message = f"Error from {role['name']} ({model_name}): {e}"
        print(error_message) # Still print to console for debugging
        return f"Error occurred during response generation for {role['name']}. Please check console for details."


async def evaluate_responses(responses, eval_model_name, eval_temperature_setting):
    """
    Evaluates responses from different expert roles using a senior manager perspective.
    Extracts key elements like perfect answer and illustration prompt using regex for robustness.
    Provides detailed console output for debugging and monitoring.
    """
    temperature = temperature_presets.get(eval_temperature_setting, 0.7) # Default to 'Balanced'
    responses_text = "\n".join([f"{role_name} Response: {response}\n" for role_name, response in responses.items()])

    prompt = (
        "As the Senior Manager, please review and evaluate the following responses from junior managers based on clarity, relevance, depth of information, and practicality. "
        "Consider the target audience for each response (e.g., technical vs. general public).\n\n"
        f"{responses_text}\n"
        "Provide your evaluation and elaborate on the findings. Which response is the most compelling and why? Are there any responses that are misleading or inaccurate? "
        "Finally, provide a concise summary of the key takeaways.\n\n"
        "Also provide a perfect answer to the question. Lastly, craft a prompt to create a custom illustration depicting the key concepts and insights from the responses."
    )

    try:
        ollama.temperature = temperature
        evaluation_response = await asyncio.to_thread(ollama.chat, model=eval_model_name, messages=[{'role': 'user', 'content': prompt}])
        evaluation_content = evaluation_response['message']['content']

        perfect_answer_match = re.search(r"Perfect Answer:\s*(.+?)(?=(Illustration Prompt:|Summary:|Evaluation:|Key Takeaways:|$))", evaluation_content, re.DOTALL | re.IGNORECASE)
        illustration_prompt_match = re.search(r"Illustration Prompt:\s*(.+?)(?=(Summary:|Evaluation:|Key Takeaways:|$))", evaluation_content, re.DOTALL | re.IGNORECASE)

        perfect_answer = perfect_answer_match.group(1).strip() if perfect_answer_match else "Perfect answer not found in evaluation."
        illustration_prompt = illustration_prompt_match.group(1).strip() if illustration_prompt_match else "Illustration prompt not found in evaluation."

        print("\n--- Evaluation Details (Console Output) ---") # Clearer console output
        print("Perfect Answer:", perfect_answer)
        print("Illustration Prompt:", illustration_prompt)
        print("Full Evaluation Output:\n", evaluation_content) # Display full output for debugging
        print("--- End Evaluation Details ---")

        return evaluation_content, perfect_answer, illustration_prompt

    except Exception as e:
        error_message = f"Error during evaluation process: {e}"
        print(error_message)
        return "Error in evaluation. Please check console.", "Error extracting perfect answer.", "Error extracting illustration prompt."


# --- Gradio Interface Function ---
async def gradio_interface(question, role1, role2, role3, role4, model1, model2, model3, model4, eval_model, temp_setting1, temp_setting2, temp_setting3, temp_setting4, eval_temp_setting):
    """
    Main function for the Gradio interface.
    Handles user input, generates expert responses, evaluates them, and returns outputs for display.
    """
    selected_roles = [role1, role2, role3, role4]
    selected_models = [model1, model2, model3, model4]
    selected_temp_settings = [temp_setting1, temp_setting2, temp_setting3, temp_setting4]

    expert_responses = {}
    tasks = []

    for i in range(4):
        if selected_roles[i]:
            role = selected_roles[i]
            model_name = selected_models[i]
            temp_setting = selected_temp_settings[i]
            tasks.append(generate_expert_response(question, role, model_name, temp_setting)) # Using utility function

    results = await asyncio.gather(*tasks)

    k = 0 # Index to track results
    for i in range(4):
        if selected_roles[i]:
            role_name = selected_roles[i]['name']
            expert_responses[role_name] = results[k]
            k += 1

    evaluation_text, perfect_answer_text, illustration_prompt_text = await evaluate_responses(expert_responses, eval_model, eval_temp_setting) # Using utility function

    response_texts = [expert_responses.get(role['name'], "") if role else "" for role in selected_roles] # List comprehension for conciseness

    return *response_texts, evaluation_text, perfect_answer_text, illustration_prompt_text # Correct unpacking


# --- Gradio Interface Definition ---
iface = gr.Interface(
    fn=gradio_interface,
    inputs=[
        gr.Textbox(label="Pose your question here"), # More descriptive label
        gr.Dropdown(possible_roles, label="Expert Role 1", info="Choose the first Expert role."), # Added info
        gr.Dropdown(possible_roles, label="Expert Role 2", info="Choose the second Expert role."),
        gr.Dropdown(possible_roles, label="Expert Role 3", info="Choose the third Expert role."),
        gr.Dropdown(possible_roles, label="Expert Role 4", info="Choose the fourth Expert role."),
        gr.Dropdown(model_options, label="Model for Role 1", info="Select the language model for Expert 1."), # More descriptive labels and info
        gr.Dropdown(model_options, label="Model for Role 2", info="Select model for Expert 2."),
        gr.Dropdown(model_options, label="Model for Role 3", info="Select model for Expert 3."),
        gr.Dropdown(model_options, label="Model for Role 4", info="Select model for Expert 4."),
        gr.Dropdown(evaluation_model_options, label="Evaluation Model", info="Choose the model for senior manager evaluation."), # Specific evaluation model dropdown
        gr.Dropdown(list(temperature_presets.keys()), label="Approach style  Role 1", info="Set approach for Expert 1 (Cautious, Balanced, Creative)."), # More descriptive temperature labels
        gr.Dropdown(list(temperature_presets.keys()), label="Approach style  Role 2", info="Set approach for Expert 2."),
        gr.Dropdown(list(temperature_presets.keys()), label="Approach style  Role 3", info="Set approach for Expert 3."),
        gr.Dropdown(list(temperature_presets.keys()), label="Approach style  Role 4", info="Set approach for Expert 4."),
        gr.Dropdown(list(temperature_presets.keys()), label="Approach style ", info="Set approach for Senior Manager evaluation."),
        

    ],
    outputs=[
        gr.Textbox(label="Response from Expert 1"), # More descriptive output labels
        gr.Textbox(label="Response from Expert 2"),
        gr.Textbox(label="Response from Expert 3"),
        gr.Textbox(label="Response from Expert 4"),
        gr.Textbox(label="Senior Manager Evaluation", lines=10), # Increased lines for better readability
        gr.Textbox(label="Perfect Answer (from Evaluation)", lines=3), # Clarified label
        gr.Textbox(label="Illustration Prompt (from Evaluation)", lines=3), # Clarified label
    ],
    title="Ask the Experts: Multi-Perspective Response System", # More engaging title
    description="""
    This tool simulates a team of experts providing answers to your questions from different perspectives. 
    Select up to four expert roles, each with a specific focus (e.g., Strategic, Technical, UX, Ethical). 
    Choose language models and temperature settings for each expert and an evaluation model for the 'Senior Manager' who reviews all responses, provides a perfect answer, and suggests an illustration prompt.
    """, # More detailed and user-friendly description
    examples=[ # Example questions to guide users
        ["What are the benefits and risks of implementing AI in customer service?"],
        ["How can we improve user engagement with our mobile app?"],
        ["Discuss the ethical implications of using facial recognition technology."],
        ["Analyze the potential market for a new eco-friendly product."],
    ],
    live=False, # Consider setting to False for performance in some environments
)


if __name__ == "__main__":
    iface.launch()
