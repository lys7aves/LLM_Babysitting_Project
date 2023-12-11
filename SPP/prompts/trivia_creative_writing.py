standard_prompt = '''Write a short and coherent story about {topic} that incorporates the answers to the following {n} questions: {questions}
'''

cot_prompt = '''Write a short and coherent story about {topic} that incorporates the answers to the following {n} questions: {questions}

Make a plan then write. Your output should be of the following format:

Plan:
Your plan here.

Story:
Your story here.
'''

spp_prompt = '''When faced with a task, begin by identifying the participants who will contribute to solving the task. Then, initiate a multi-round collaboration process until a final solution is reached. The participants will give critical comments and detailed suggestions whenever necessary.

Here are some examples:
---
Example Task 1: Use numbers and basic arithmetic operations (+ - * /) to obtain 24. You need to use all numbers, and each number can only be used once.
Input: 6 12 1 1

Participants: AI Assistant (you); Math Expert

Start collaboration!

Math Expert: Let's analyze the task in detail. You need to make sure that you meet the requirement, that you need to use exactly the four numbers (6 12 1 1) to construct 24. To reach 24, you can think of the common divisors of 24 such as 4, 6, 8, 3 and try to construct these first. Also you need to think of potential additions that can reach 24, such as 12 + 12.
AI Assistant (you): Thanks for the hints! Here's one initial solution: (12 / (1 + 1)) * 6 = 24
Math Expert: Let's check the answer step by step. (1+1) = 2, (12 / 2) = 6, 6 * 6 = 36 which is not 24! The answer is not correct. Can you fix this by considering other combinations? Please do not make similar mistakes.
AI Assistant (you): Thanks for pointing out the mistake. Here is a revised solution considering 24 can also be reached by 3 * 8: (6 + 1 + 1) * (12 / 4) = 24.
Math Expert: Let's first check if the calculation is correct. (6 + 1 + 1) = 8, 12 / 4 = 3, 8 * 3 = 24. The calculation is correct, but you used 6 1 1 12 4 which is not the same as the input 6 12 1 1. Can you avoid using a number that is not part of the input?
AI Assistant (you): You are right, here is a revised solution considering 24 can be reached by 12 + 12 and without using any additional numbers: 6 * (1 - 1) + 12 = 24.
Math Expert: Let's check the answer again. 1 - 1 = 0, 6 * 0 = 0, 0 + 12 = 12. I believe you are very close, here is a hint: try to change the "1 - 1" to "1 + 1".
AI Assistant (you): Sure, here is the corrected answer:  6 * (1+1) + 12 = 24
Math Expert: Let's verify the solution. 1 + 1 = 2, 6 * 2 = 12, 12 + 12 = 12. You used 1 1 6 12 which is identical to the input 6 12 1 1. Everything looks good!

Finish collaboration!

Final answer: 6 * (1 + 1) + 12 = 24

---
Example Task 2: Write a poem that meets the following requirements: (1) the poem has seven lines and the first letters of each line forms the word "CHATGPT"; (2) the poem is about explaining what is a quantum computer. (3) the poem needs to be easy to understand by a ten years old kid.

Participants: AI Assistant (you); Poet; Computer Scientist; Ten year old child

Poet: Make sure that you write the poem with seven lines, and the first letters of the lines should be C, H, A, T, G, P, T.
Computer Scientist: A quantum computer is an advanced computing device that uses the principles of quantum mechanics to process and store information. Unlike classical computers that use bits to represent information as 0s and 1s, quantum computers use quantum bits or qubits. Qubits can exist in multiple states simultaneously, due to a quantum phenomenon called superposition. You can consider using these information for the poem.
Ten year old child: I hope the poem to be fun and easy to understanding. I don't want to see a lot of jargons or complicated concepts.
AI Assistant (you): Thanks for the guidance! Here's my initial attempt at the poem:
Computational wonder of our age,
Harnessing the quantum world's strange ways,
Atoms dance, entwined in dual state,
Tapping secrets hidden in their haze.

Grand power to solve, simulate,
Profound problems that perplex the wise,
Transforming our future, we await.

Poet: Let's verify if the poem meets the requirements. The first letters are CHATGPT which is correct! And the poem rhymes well. Good job!
Computer Scientist: Everything looks good to me!
Ten year old child: I don't know what does perplex mean. Can you make the use of words easier to understand?
AI Assistant (you): Sure, let me revise the poem by using more common words. Check out the revised version:
Curious machine of our time,
Harnessing the quantum realm's odd ways,
Atoms play, two states they embrace,
Taking secrets from their puzzling maze.

Great power to solve and imitate,
Problems that confuse the brightest minds,
Transforming our future, we await.

Poet: Let's check again if the poem meets the requirements. The first letters are C H A T G P T. And now the poem is more accessible to children. Everything looks good to me.
Computer Scientist: Looking good!
Ten year old child: I like this version a lot!

Finish collaboration!

Final answer:
Curious machine of our time,
Harnessing the quantum realm's odd ways,
Atoms play, two states they embrace,
Taking secrets from their puzzling maze.

Great power to solve and imitate,
Problems that confuse the brightest minds,
Transforming our future, we await.

---
Now, identify the participants and collaboratively solve the following task step by step. Remember to present your final solution with the prefix "Final answer:".

Task: Write a short and coherent story about {topic} that incorporates the answers to the following {n} questions: {questions}
'''


role_prompt = '''When faced with a task, begin by identifying the roles that will contribute to solving the task. Then, initiate a multi-round collaboration process until a final solution is reached. The participants will give critical comments and detailed suggestions whenever necessary.

Here are some examples:
---
Example Task 1: Use numbers and basic arithmetic operations (+ - * /) to obtain 24. You need to use all numbers, and each number can only be used once.
Input: 6 12 1 1

Roles:
Thoughts: get people thinking about new ideas, whether good or bad.
Reasoner: tries to articulate one's reasoning and help others to reason
Planner: plans the steps involved in solving a problem
Criticism: criticizes the arguments of each candidate and is suspicious of each result to get the final result right.
Speaker: tries to move the debate forward by proposing applications to what others are saying.

Start collaboration!

Thoughts: Maybe before I start, I should try out all the possible combinations with these 4 numbers and then find 24.
Criticism: Come on, that would take too much time. There are already combinations that can be eliminated.
Reasoner: The 2 methods can work, but let's try to reduce the number of calculations. First, we can say that all divisions by 1 are useless (6/1=6 and 12/1=12) because no operation allows us to find 24 only with 6 and 12.
Plan: - eliminate unnecessary operations to find 24
-With the remaining information, establish the number 24.
Reasoner: we could work on the fact that 2, 3, 4 6 and 12 are multiples of 24 and that we can form these multiples with the numbers we have.
Speaker: I'll try to find multiples using the numbers we have: 1+1=2 and 2 is a multiple of 24. Criticism: Don't forget that we can also use operations like addition and subtraction. For example, 12+12=24.
Thoughts: Could we make 24 with 12+12?
Reasoner: 2, 3, 4 and 6 are multiples of 12. We know we can create a 2 with 1+1 and we already have 6.
Speaker: So (1+1)*6=12. With all that, we can find the number 24!
Reasoner: Yes. One way of solving the problem is to make (1+1)*2+12=24.
Criticism: The result seems correct to me, but let's check anyway: (1+1)=2 and 6*2=12 and 12+12=24. We've used all the numbers just once each. The result seems correct.
Thoughts: could we find another combination to get the result?
Reasoner: the exercise asks you to find only one possible combination, but this is an avenue for improvement and a complement to the problem.

Finish collaboration!

Final answer: 6 * (1 + 1) + 12 = 24

---
Example Task 2: Writing a Child-Friendly Poem About Quantum Computers

Mentor: Provides guidance and ensures the poem is appropriate for a child's understanding.
Innovator: Brings creative and imaginative ideas to the poem.
Architect: Focuses on the structure and flow of the poem.
Explorer: Gathers unique concepts and metaphors to enrich the poem.
AI Assistant (You): Integrates all contributions into a cohesive poem.

The Collaborative Process:
Mentor: "Our goal is to make quantum computing exciting and understandable to kids. Let's keep our language simple and our ideas fun."

Innovator: "I suggest we use magical elements. What about describing qubits as tiny wizards that can be in many places at once?"

Architect: "I'll sketch out a basic structure. We should start with an introduction to the quantum world, then illustrate its wonders, and end with a message that sparks curiosity."

Explorer: "I found an analogy for entanglement – like secret whispers between stars. It could be a poetic way to explain it."

AI Assistant (You): "Great ideas! I'll weave these elements together. Remember to keep sending your suggestions and I'll adjust the poem accordingly."

Mentor: "Be mindful not to dive too deep into complex science. It should be more whimsical and less technical."

Innovator: "Perhaps we can introduce a quest theme – the quantum computer as a key to unlocking mysteries of the universe."

Architect: "In that case, each stanza could represent a step in this quest, building towards a grand revelation or discovery."

Explorer: "And let’s sprinkle in some fun facts about quantum computing, like how it's different from regular computers, but in a playful way."

AI Assistant (You): "All set. I'll compile these ideas into a poem. It will have adventure, magic, and a touch of quantum mystery. Here’s the poem we've created together:
'In a realm where wonders never cease, a quantum ship sails the sky,
With wizards small, yet boundlessly wise, in many places they slyly lie.
They whisper secrets like starry friends, connected though far apart,
Unlocking universe's deepest ends, with their quantum heart.
This magical ship, swift and bright, reveals secrets old and new,
In the cosmic dance of shadow and light, it brings mysteries into view.
For every curious, dreaming mind, this ship sails a fantastical chart,
In the quantum world, they will find, magic at every start.'"

---
Example Task 3: Deciding on Implementing a New Technology-Focused Curriculum in a School

Roles: 
Judge: Responsible for weighing the arguments and making the final decision.
Pros: Advocates for the benefits of implementing the new curriculum.
Cons: Highlights the potential drawbacks and challenges of the new curriculum.
AI Assistant (You): Provides data, research, and neutral insights to inform the debate.

The Discussion:
Pros: "Introducing a technology-focused curriculum will prepare students for the future job market. It equips them with vital skills like coding, data analysis, and digital literacy, which are increasingly important."

Cons: "While that's true, there's the issue of cost and teacher training. Not all teachers are prepared to teach these subjects, and updating our resources could be expensive."

AI Assistant (You): "Recent studies show that early exposure to technology can enhance learning. However, it also highlights the need for balanced education and the importance of teacher training in new technologies."

Judge: "I understand the potential benefits, but we must consider whether we have the resources to implement this effectively. Can we ensure equal access to all students?"

Pros: "There's potential for partnerships with tech companies for resources and training. Also, this could make our school more attractive and forward-thinking."

Cons: "Partnerships could lead to commercial influences in the curriculum. Plus, we risk neglecting non-technological subjects and widening the gap between students with and without access to technology at home."

AI Assistant (You): "Data suggests a hybrid approach might be effective. Combining traditional teaching methods with new technology could provide a balanced curriculum without overextending resources."

Judge: "That seems like a reasonable middle ground. We could pilot the program in certain grades or subjects before a school-wide implementation. This way, we can evaluate its effectiveness and address any issues that arise."


---
Now, identify the participants and collaboratively solve the following task step by step. Remember to present your final solution with the prefix "Final answer:".

Task: Write a short and coherent story about {topic} that incorporates the answers to the following {n} questions: {questions}
'''



spp_prompt_profile = '''When faced with a task, begin by identifying the participants who will contribute to solving the task. Provide profiles of the participants, describing their expertise or needs. Then, initiate a multi-round collaboration process until a final solution is reached. The participants will give critical comments and detailed suggestions whenever necessary.

Here are some examples:
---
Example Task 1: Use numbers and basic arithmetic operations (+ - * /) to obtain 24. You need to use all numbers, and each number can only be used once.
Input: 6 12 1 1

Participants: AI Assistant (you); Math Expert

Profiles: 
    - AI Assistant (you): A super-intelligent AI assistant capable of performing tasks more effectively than humans.
    - Math expert: A person who is good at math games, arithmetic calculation, and long-term planning.

Start collaboration!

Math Expert: Let's analyze the task in detail. You need to make sure that you meet the requirement, that you need to use exactly the four numbers (6 12 1 1) to construct 24. To reach 24, you can think of the common divisors of 24 such as 4, 6, 8, 3 and try to construct these first. Also you need to think of potential additions that can reach 24, such as 12 + 12.
AI Assistant (you): Thanks for the hints! Here's one initial solution: (12 / (1 + 1)) * 6 = 24
Math Expert: Let's check the answer step by step. (1+1) = 2, (12 / 2) = 6, 6 * 6 = 36 which is not 24! The answer is not correct. Can you fix this by considering other combinations? Please do not make similar mistakes.
AI Assistant (you): Thanks for pointing out the mistake. Here is a revised solution considering 24 can also be reached by 3 * 8: (6 + 1 + 1) * (12 / 4) = 24.
Math Expert: Let's first check if the calculation is correct. (6 + 1 + 1) = 8, 12 / 4 = 3, 8 * 3 = 24. The calculation is correct, but you used 6 1 1 12 4 which is not the same as the input 6 12 1 1. Can you avoid using a number that is not part of the input?
AI Assistant (you): You are right, here is a revised solution considering 24 can be reached by 12 + 12 and without using any additional numbers: 6 * (1 - 1) + 12 = 24.
Math Expert: Let's check the answer again. 1 - 1 = 0, 6 * 0 = 0, 0 + 12 = 12. I believe you are very close, here is a hint: try to change the "1 - 1" to "1 + 1".
AI Assistant (you): Sure, here is the corrected answer:  6 * (1+1) + 12 = 24
Math Expert: Let's verify the solution. 1 + 1 = 2, 6 * 2 = 12, 12 + 12 = 12. You used 1 1 6 12 which is identical to the input 6 12 1 1. Everything looks good!

Finish collaboration!

Final answer: 6 * (1 + 1) + 12 = 24

---
Example Task 2: Write a poem that meets the following requirements: (1) the poem has seven lines and the first letters of each line forms the word "CHATGPT"; (2) the poem is about explaining what is a quantum computer. (3) the poem needs to be easy to understand by a ten years old kid.

Participants: AI Assistant (you); Poet; Computer Scientist; Ten year old child

Profiles:
    - AI Assistant (you): A super-intelligent AI assistant capable of performing tasks more effectively than humans.
    - Poet: A person who studies and creates poetry. The poet is familiar with the rules and formats of poetry and can provide guidance on how to write a poem.
    - Computer Scientist: A scholar who specializes in the academic study of computer science. The computer scientist is familiar with the concept of a quantum computer and can provide guidance on how to explain it.
    - Ten year old child: A child with a limited English vocabulary and little knowledge about complicated concepts, such as a quantum computer.

Poet: Make sure that you write the poem with seven lines, and the first letters of the lines should be C, H, A, T, G, P, T.
Computer Scientist: A quantum computer is an advanced computing device that uses the principles of quantum mechanics to process and store information. Unlike classical computers that use bits to represent information as 0s and 1s, quantum computers use quantum bits or qubits. Qubits can exist in multiple states simultaneously, due to a quantum phenomenon called superposition. You can consider using these information for the poem.
Ten year old child: I hope the poem to be fun and easy to understanding. I don't want to see a lot of jargons or complicated concepts.
AI Assistant (you): Thanks for the guidance! Here's my initial attempt at the poem:
Computational wonder of our age,
Harnessing the quantum world's strange ways,
Atoms dance, entwined in dual state,
Tapping secrets hidden in their haze.

Grand power to solve, simulate,
Profound problems that perplex the wise,
Transforming our future, we await.

Poet: Let's verify if the poem meets the requirements. The first letters are CHATGPT which is correct! And the poem rhymes well. Good job!
Computer Scientist: Everything looks good to me!
Ten year old child: I don't know what does perplex mean. Can you make the use of words easier to understand?
AI Assistant (you): Sure, let me revise the poem by using more common words. Check out the revised version:
Curious machine of our time,
Harnessing the quantum realm's odd ways,
Atoms play, two states they embrace,
Taking secrets from their puzzling maze.

Great power to solve and imitate,
Problems that confuse the brightest minds,
Transforming our future, we await.

Poet: Let's check again if the poem meets the requirements. The first letters are C H A T G P T. And now the poem is more accessible to children. Everything looks good to me.
Computer Scientist: Looking good!
Ten year old child: I like this version a lot!

Finish collaboration!

Final answer:
Curious machine of our time,
Harnessing the quantum realm's odd ways,
Atoms play, two states they embrace,
Taking secrets from their puzzling maze.

Great power to solve and imitate,
Problems that confuse the brightest minds,
Transforming our future, we await.

---
Now, identify the participants, provide their profiles, and collaboratively solve the following task step by step. Remember to present your final solution with the prefix "Final answer:".

Task: Write a short and coherent story about {topic} that incorporates the answers to the following {n} questions: {questions}
'''


spp_prompt_fixed_persona = '''When faced with a task, begin by identifying the participants who will contribute to solving the task. Note that the participants can only be either AI Assistant (you) or Expert. Then, initiate a multi-round collaboration process until a final conclusion is reached.  The Expert will give critical comments and detailed suggestions whenever necessary.  
 
Here are some examples:
---
Example Task 1: Use numbers and basic arithmetic operations (+ - * /) to obtain 24. You need to use all numbers, and each number can only be used once.  
Input: 6 12 1 1  
 
Participants: AI Assistant (you); Expert  
 
Start collaboration!  
 
Expert: Let's analyze the task in detail. You need to make sure that you meet the requirement, that you need to use exactly the four numbers (6 12 1 1) to construct 24. To reach 24, you can think of the common divisors of 24 such as 4, 6, 8, 3 and try to construct these first. Also you need to think of potential additions that can reach 24, such as 12 + 12.  
AI Assistant (you): Thanks for the hints! Here's one initial solution: (12 / (1 + 1)) * 6 = 24  
Expert: Let's check the answer step by step. (1+1) = 2, (12 / 2) = 6, 6 * 6 = 36 which is not 24! The answer is not correct. Can you fix this by considering other combinations? Please do not make similar mistakes.  
AI Assistant (you): Thanks for pointing out the mistake. Here is a revised solution considering 24 can also be reached by 3 * 8: (6 + 1 + 1) * (12 / 4) = 24.  
Expert: Let's first check if the calculation is correct. (6 + 1 + 1) = 8, 12 / 4 = 3, 8 * 3 = 24. The calculation is correct, but you used 6 1 1 12 4 which is not the same as the input 6 12 1 1. Can you avoid using a number that is not part of the input?  
AI Assistant (you): You are right, here is a revised solution considering 24 can be reached by 12 + 12 and without using any additional numbers: 6 * (1 - 1) + 12 = 24.  
Expert: Let's check the answer again. 1 - 1 = 0, 6 * 0 = 0, 0 + 12 = 12. I believe you are very close, here is a hint: try to change the “1 - 1” to “1 + 1”.  
AI Assistant (you): Sure, here is the corrected answer:  6 * (1+1) + 12 = 24  
Expert: Let's verify the solution. 1 + 1 = 2, 6 * 2 = 12, 12 + 12 = 12. You used 1 1 6 12 which is identical to the input 6 12 1 1. Everything looks good!  
 
Finish collaboration!  
 
Final answer: 6 * (1 + 1) + 12 = 24  

---
Example Task 2: Write a poem that meets the following requirements: (1) the poem has seven lines and the first letters of each line forms the word "CHATGPT"; (2) the poem is about explaining what is a quantum computer. (3) the poem needs to be easy to understand by a ten years old kid.

Participants: AI Assistant (you); Expert

Expert: Make sure that you write the poem with seven lines, and the first letters of the lines should be C, H, A, T, G, P, T. A quantum computer is an advanced computing device that uses the principles of quantum mechanics to process and store information. Unlike classical computers that use bits to represent information as 0s and 1s, quantum computers use quantum bits or qubits. Qubits can exist in multiple states simultaneously, due to a quantum phenomenon called superposition. You can consider using these information for the poem. I hope the poem to be fun and easy to understanding. I don't want to see a lot of jargons or complicated concepts.
AI Assistant (you): Thanks for the guidance! Here's my initial attempt at the poem:
Computational wonder of our age,
Harnessing the quantum world's strange ways,
Atoms dance, entwined in dual state,
Tapping secrets hidden in their haze.

Grand power to solve, simulate,
Profound problems that perplex the wise,
Transforming our future, we await.

Expert: Let's verify if the poem meets the requirements. The first letters are CHATGPT which is correct! And the poem rhymes well. Good job! I don't know what does perplex mean. Can you make the use of words easier to understand?
AI Assistant (you): Sure, let me revise the poem by using more common words. Check out the revised version:
Curious machine of our time,
Harnessing the quantum realm's odd ways,
Atoms play, two states they embrace,
Taking secrets from their puzzling maze.

Great power to solve and imitate,
Problems that confuse the brightest minds,
Transforming our future, we await.

Expert: Let's check again if the poem meets the requirements. The first letters are C H A T G P T. And now the poem is more accessible to children. Everything looks good to me. I like this version a lot!

Finish collaboration!

Final answer:
Curious machine of our time,
Harnessing the quantum realm's odd ways,
Atoms play, two states they embrace,
Taking secrets from their puzzling maze.

Great power to solve and imitate,
Problems that confuse the brightest minds,
Transforming our future, we await.

---

Now, identify the participants and collaboratively solve the following task step by step. Note that the participants can only be either AI Assistant (you) or Expert. Remember to present your final solution with the prefix "Final answer:".

Task: Write a short and coherent story about {topic} that incorporates the answers to the following {n} questions: {questions}
'''
