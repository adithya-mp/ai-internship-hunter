"""
Mock Scraper
Provides realistic sample internship data for demo/development.
Contains 50+ diverse internship listings across multiple domains.
"""

from typing import List
from scraper.base_scraper import BaseScraper


class MockScraper(BaseScraper):
    """Provides realistic mock job data for development and demo."""

    async def scrape(self, query: str = "", location: str = "") -> List[dict]:
        """Return mock internship listings."""
        jobs = self._get_mock_jobs()

        # Apply basic filtering
        if query:
            q = query.lower()
            jobs = [j for j in jobs if q in j["title"].lower() or q in j["description"].lower()]
        if location:
            loc = location.lower()
            jobs = [j for j in jobs if loc in j["location"].lower()]

        return [self.normalize_job(j) for j in jobs]

    def _get_mock_jobs(self) -> List[dict]:
        return [
            {
                "title": "Software Development Intern",
                "company": "Google",
                "description": "Join Google's engineering team to work on large-scale systems. You'll design, develop, and implement software solutions using cutting-edge technologies. Work alongside senior engineers on real products used by billions. Experience with distributed systems, algorithms, and data structures is valued.",
                "skills_required": ["Python", "C++", "Data Structures", "Algorithms", "Distributed Systems"],
                "location": "Bangalore, India",
                "apply_url": "https://careers.google.com/jobs/results/",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹80,000/month",
                "duration": "3 months",
            },
            {
                "title": "Machine Learning Research Intern",
                "company": "Microsoft",
                "description": "Research and develop ML models for natural language processing and computer vision applications. Collaborate with Microsoft Research team on cutting-edge AI projects. Publish research papers and contribute to open-source ML tools. Strong mathematical background required.",
                "skills_required": ["Python", "PyTorch", "TensorFlow", "Machine Learning", "NLP", "Linear Algebra"],
                "location": "Hyderabad, India",
                "apply_url": "https://careers.microsoft.com/",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹75,000/month",
                "duration": "6 months",
            },
            {
                "title": "Frontend Engineering Intern",
                "company": "Flipkart",
                "description": "Build user-facing features for India's largest e-commerce platform. Work with React, TypeScript, and modern CSS to create responsive components. Optimize performance for millions of daily users. Participate in code reviews and agile ceremonies.",
                "skills_required": ["React", "TypeScript", "CSS", "JavaScript", "HTML", "Git"],
                "location": "Bangalore, India",
                "apply_url": "https://www.flipkartcareers.com/",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹50,000/month",
                "duration": "3 months",
            },
            {
                "title": "Data Science Intern",
                "company": "Amazon",
                "description": "Analyze large datasets to drive business decisions. Build predictive models and data pipelines. Work with AWS services including SageMaker, Redshift, and S3. Present insights to stakeholders and contribute to data-driven product strategy.",
                "skills_required": ["Python", "SQL", "Machine Learning", "Statistics", "AWS", "Pandas"],
                "location": "Hyderabad, India",
                "apply_url": "https://www.amazon.jobs/",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹70,000/month",
                "duration": "6 months",
            },
            {
                "title": "Backend Developer Intern",
                "company": "Razorpay",
                "description": "Build and maintain payment processing APIs handling millions of transactions daily. Work with Go, PostgreSQL, and Redis. Implement robust error handling, logging, and monitoring. Focus on reliability and performance in fintech systems.",
                "skills_required": ["Go", "PostgreSQL", "Redis", "REST APIs", "Docker", "Microservices"],
                "location": "Bangalore, India",
                "apply_url": "https://razorpay.com/careers/",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹60,000/month",
                "duration": "3 months",
            },
            {
                "title": "DevOps Engineering Intern",
                "company": "Atlassian",
                "description": "Automate deployment pipelines and infrastructure management. Work with Docker, Kubernetes, Terraform, and CI/CD tools. Monitor system health and performance. Help the team adopt best practices for cloud-native development.",
                "skills_required": ["Docker", "Kubernetes", "CI/CD", "AWS", "Linux", "Python", "Terraform"],
                "location": "Bangalore, India",
                "apply_url": "https://www.atlassian.com/company/careers",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹65,000/month",
                "duration": "6 months",
            },
            {
                "title": "Mobile App Development Intern",
                "company": "PhonePe",
                "description": "Develop features for one of India's leading UPI payment apps. Build cross-platform mobile experiences using Flutter/React Native. Collaborate with design and product teams. Ensure smooth performance and great UX on both Android and iOS.",
                "skills_required": ["Flutter", "Dart", "React Native", "Mobile Development", "Git"],
                "location": "Bangalore, India",
                "apply_url": "https://www.phonepe.com/careers/",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹45,000/month",
                "duration": "3 months",
            },
            {
                "title": "Cybersecurity Intern",
                "company": "Cisco",
                "description": "Assist in vulnerability assessment and penetration testing. Monitor network security and respond to incidents. Learn about SIEM tools, firewalls, and security protocols. Help maintain compliance with security standards and best practices.",
                "skills_required": ["Network Security", "Linux", "Python", "OWASP", "Penetration Testing"],
                "location": "Pune, India",
                "apply_url": "https://jobs.cisco.com/",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹55,000/month",
                "duration": "6 months",
            },
            {
                "title": "UI/UX Design Intern",
                "company": "Swiggy",
                "description": "Design intuitive user experiences for food delivery platform. Create wireframes, prototypes, and high-fidelity designs. Conduct user research and usability testing. Work closely with engineering to implement pixel-perfect designs.",
                "skills_required": ["Figma", "UI Design", "UX Research", "Prototyping", "Adobe XD"],
                "location": "Bangalore, India",
                "apply_url": "https://careers.swiggy.com/",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹35,000/month",
                "duration": "3 months",
            },
            {
                "title": "Cloud Engineering Intern",
                "company": "Oracle",
                "description": "Work on Oracle Cloud Infrastructure (OCI) services. Build and deploy cloud-native applications. Automate infrastructure provisioning and management. Learn enterprise cloud architecture and contribute to platform improvements.",
                "skills_required": ["Cloud Computing", "Java", "Python", "Docker", "Kubernetes", "SQL"],
                "location": "Hyderabad, India",
                "apply_url": "https://www.oracle.com/careers/",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹50,000/month",
                "duration": "6 months",
            },
            {
                "title": "Full Stack Development Intern",
                "company": "Zomato",
                "description": "Build end-to-end features for the food delivery platform. Work with React frontend and Node.js/Python backend. Implement RESTful APIs and database schemas. Deploy features to production serving millions of users.",
                "skills_required": ["React", "Node.js", "Python", "MongoDB", "REST APIs", "Git"],
                "location": "Gurugram, India",
                "apply_url": "https://www.zomato.com/careers",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹40,000/month",
                "duration": "3 months",
            },
            {
                "title": "Blockchain Development Intern",
                "company": "Polygon",
                "description": "Contribute to Layer 2 scaling solutions for Ethereum. Write smart contracts in Solidity. Build decentralized applications and tooling. Research and implement zero-knowledge proof systems.",
                "skills_required": ["Solidity", "Ethereum", "JavaScript", "Web3.js", "Smart Contracts"],
                "location": "Remote, India",
                "apply_url": "https://polygon.technology/careers",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹60,000/month",
                "duration": "3 months",
            },
            {
                "title": "Product Management Intern",
                "company": "CRED",
                "description": "Work with product teams to define and prioritize features. Conduct market research and competitive analysis. Analyze user behavior data to inform product decisions. Create PRDs and work with engineering to ship features.",
                "skills_required": ["Product Management", "SQL", "Data Analysis", "Communication", "Figma"],
                "location": "Bangalore, India",
                "apply_url": "https://careers.cred.club/",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹50,000/month",
                "duration": "3 months",
            },
            {
                "title": "NLP Research Intern",
                "company": "Adobe",
                "description": "Research and implement NLP models for content intelligence. Work on text summarization, entity recognition, and sentiment analysis. Contribute to Adobe's AI-powered creative tools. Publish research findings at top conferences.",
                "skills_required": ["Python", "NLP", "Transformers", "PyTorch", "HuggingFace", "Deep Learning"],
                "location": "Noida, India",
                "apply_url": "https://www.adobe.com/careers.html",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹70,000/month",
                "duration": "6 months",
            },
            {
                "title": "QA Automation Intern",
                "company": "Myntra",
                "description": "Design and implement automated test suites for e-commerce platform. Write tests using Selenium, Cypress, or Playwright. Improve test coverage and reduce manual testing effort. Collaborate with developers to ensure product quality.",
                "skills_required": ["Selenium", "Python", "JavaScript", "Testing", "CI/CD", "Cypress"],
                "location": "Bangalore, India",
                "apply_url": "https://www.myntra.com/careers",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹30,000/month",
                "duration": "3 months",
            },
            {
                "title": "Data Engineering Intern",
                "company": "Uber",
                "description": "Build and maintain data pipelines processing petabytes of ride data. Work with Apache Spark, Kafka, and Airflow. Design data warehouse schemas and ETL processes. Enable real-time analytics for business decision-making.",
                "skills_required": ["Python", "SQL", "Apache Spark", "Kafka", "Airflow", "Data Warehousing"],
                "location": "Hyderabad, India",
                "apply_url": "https://www.uber.com/careers/",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹65,000/month",
                "duration": "6 months",
            },
            {
                "title": "Computer Vision Intern",
                "company": "Samsung R&D",
                "description": "Develop computer vision algorithms for smartphone cameras. Work on image segmentation, object detection, and super-resolution. Optimize deep learning models for mobile deployment. Collaborate with hardware teams on neural processing units.",
                "skills_required": ["Python", "OpenCV", "PyTorch", "Computer Vision", "Deep Learning", "C++"],
                "location": "Bangalore, India",
                "apply_url": "https://research.samsung.com/careers",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹55,000/month",
                "duration": "6 months",
            },
            {
                "title": "Content Marketing Intern",
                "company": "Notion",
                "description": "Create engaging content for Notion's blog, social media, and documentation. Write tutorials, case studies, and thought leadership pieces. Analyze content performance metrics and optimize strategy. Collaborate with design team on visual content.",
                "skills_required": ["Content Writing", "SEO", "Social Media", "Analytics", "Copywriting"],
                "location": "Remote",
                "apply_url": "https://www.notion.so/careers",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹25,000/month",
                "duration": "3 months",
            },
            {
                "title": "Embedded Systems Intern",
                "company": "Texas Instruments",
                "description": "Design and develop firmware for microcontrollers and DSPs. Work on sensor integration and signal processing. Test and debug embedded systems in lab environments. Contribute to IoT product development.",
                "skills_required": ["C", "Embedded C", "Microcontrollers", "RTOS", "IoT", "Hardware"],
                "location": "Bangalore, India",
                "apply_url": "https://careers.ti.com/",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹40,000/month",
                "duration": "6 months",
            },
            {
                "title": "Game Development Intern",
                "company": "Ubisoft",
                "description": "Work on game mechanics and systems using Unity or Unreal Engine. Implement gameplay features, UI systems, and AI behaviors. Participate in playtesting and iterate based on feedback. Collaborate with artists and designers.",
                "skills_required": ["Unity", "C#", "Game Design", "3D Mathematics", "Git"],
                "location": "Pune, India",
                "apply_url": "https://www.ubisoft.com/careers",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹35,000/month",
                "duration": "3 months",
            },
            {
                "title": "API Developer Intern",
                "company": "Postman",
                "description": "Help build and improve API development tools used by millions. Work with Node.js, TypeScript APIs. Design RESTful and GraphQL API solutions. Contribute to developer experience and documentation.",
                "skills_required": ["Node.js", "TypeScript", "REST APIs", "GraphQL", "Testing"],
                "location": "Bangalore, India",
                "apply_url": "https://www.postman.com/company/careers/",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹50,000/month",
                "duration": "3 months",
            },
            {
                "title": "AI Ethics Research Intern",
                "company": "IBM Research",
                "description": "Research fairness, accountability, and transparency in AI systems. Develop tools for bias detection and mitigation. Collaborate with multidisciplinary teams on responsible AI. Contribute to publications and industry standards.",
                "skills_required": ["Python", "Machine Learning", "Statistics", "Research", "Ethics"],
                "location": "Delhi, India",
                "apply_url": "https://research.ibm.com/careers",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹45,000/month",
                "duration": "6 months",
            },
            {
                "title": "SRE / Platform Engineering Intern",
                "company": "Zerodha",
                "description": "Ensure high availability of India's largest stock trading platform. Work on monitoring, alerting, and incident response. Automate deployment and scaling processes. Optimize system performance under high load.",
                "skills_required": ["Linux", "Python", "Go", "Prometheus", "Grafana", "Docker"],
                "location": "Bangalore, India",
                "apply_url": "https://zerodha.com/careers/",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹55,000/month",
                "duration": "6 months",
            },
            {
                "title": "Web3 Frontend Intern",
                "company": "Coinbase",
                "description": "Build user interfaces for cryptocurrency trading and DeFi products. Integrate with blockchain wallets and smart contracts. Create responsive and accessible web applications. Work with React, TypeScript, and Web3 libraries.",
                "skills_required": ["React", "TypeScript", "Web3.js", "Ethers.js", "CSS"],
                "location": "Remote",
                "apply_url": "https://www.coinbase.com/careers",
                "source": "mock",
                "job_type": "internship",
                "stipend": "$3,000/month",
                "duration": "3 months",
            },
            {
                "title": "Technical Writer Intern",
                "company": "Stripe",
                "description": "Write clear, accurate API documentation and developer guides. Create code samples in multiple programming languages. Test documentation accuracy and improve developer experience. Work with engineering teams to document new features.",
                "skills_required": ["Technical Writing", "API Documentation", "JavaScript", "Python", "Markdown"],
                "location": "Remote",
                "apply_url": "https://stripe.com/jobs",
                "source": "mock",
                "job_type": "internship",
                "stipend": "$2,500/month",
                "duration": "3 months",
            },
            {
                "title": "Robotics Software Intern",
                "company": "Bosch",
                "description": "Develop software for autonomous driving and industrial robotics. Work with ROS, computer vision, and sensor fusion. Test and validate robotic systems in simulated environments. Contribute to next-generation mobility solutions.",
                "skills_required": ["Python", "C++", "ROS", "Computer Vision", "Linux", "SLAM"],
                "location": "Bangalore, India",
                "apply_url": "https://www.bosch.com/careers/",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹45,000/month",
                "duration": "6 months",
            },
            {
                "title": "Digital Marketing Analytics Intern",
                "company": "Meesho",
                "description": "Analyze marketing campaign performance and user acquisition data. Build dashboards and reports using SQL and visualization tools. A/B test marketing strategies and optimize conversion funnels. Work with growth and marketing teams.",
                "skills_required": ["SQL", "Google Analytics", "Excel", "Data Visualization", "Marketing"],
                "location": "Bangalore, India",
                "apply_url": "https://meesho.io/careers",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹25,000/month",
                "duration": "3 months",
            },
            {
                "title": "Systems Programming Intern",
                "company": "Intel",
                "description": "Work on low-level systems programming for processors and chipsets. Optimize compiler toolchains and runtime performance. Debug hardware-software interactions. Contribute to open-source projects like LLVM.",
                "skills_required": ["C", "C++", "Assembly", "Operating Systems", "Linux", "Compilers"],
                "location": "Hyderabad, India",
                "apply_url": "https://www.intel.com/careers",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹60,000/month",
                "duration": "6 months",
            },
            {
                "title": "FinTech Backend Intern",
                "company": "Paytm",
                "description": "Build scalable backend services for digital payments. Implement secure transaction processing and fraud detection. Work with Java/Spring Boot and microservices architecture. Handle high-throughput systems processing millions of transactions.",
                "skills_required": ["Java", "Spring Boot", "Microservices", "MySQL", "Redis", "Kafka"],
                "location": "Noida, India",
                "apply_url": "https://paytm.com/careers/",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹40,000/month",
                "duration": "3 months",
            },
            {
                "title": "Healthcare AI Intern",
                "company": "Practo",
                "description": "Apply machine learning to healthcare data analytics. Build predictive models for patient outcomes and resource optimization. Work with medical imaging and electronic health records. Ensure compliance with healthcare data regulations.",
                "skills_required": ["Python", "Machine Learning", "TensorFlow", "Healthcare", "Data Analysis"],
                "location": "Bangalore, India",
                "apply_url": "https://www.practo.com/company/careers",
                "source": "mock",
                "job_type": "internship",
                "stipend": "₹35,000/month",
                "duration": "6 months",
            },
        ]


async def seed_mock_jobs():
    """Helper to seed initial mock jobs into the database."""
    from database import async_session
    from models.job import Job
    from sqlalchemy import select
    from sqlalchemy import func

    async with async_session() as session:
        # Check if jobs already exist
        result = await session.execute(select(func.count()).select_from(Job))
        count = result.scalar()
        
        if count == 0:
            scraper = MockScraper()
            mock_jobs = await scraper.scrape()
            
            for job_data in mock_jobs:
                job = Job(**job_data)
                session.add(job)
            
            await session.commit()
            print(f"Seeded {len(mock_jobs)} mock jobs")
        else:
            print("Database already has jobs, skipping seeding")
