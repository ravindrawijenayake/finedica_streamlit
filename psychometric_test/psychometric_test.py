# Questions for each category
questions = {
    "Money Resentment": "Believe money causes more problems in the world that it solves"
    [
        "If I have more money than most people in society, then, I do not deserve it.",
        "All rich people achieve wealth through greed and exploitation.",
        "I do not deserve to be wealthy.",
        "Caring about money makes you immoral.",
        "Rich people tke advantage of others to earn their wealth."
    ],
    "Financial Fantasists": "Believe money is the key to all life's problems"
    [
        "All problems  can be solved by spending money.",
        "You cannot be happy unless you are rich.",
        "People who are happy must be unhappy.",
        "You should always seek to have more money.",
        "Money is a way of gaining power and influence."
    ],
    "Money Prestige": "Believe that displays of wealth equate to their social standing"
    [
        "I am what I own.",
        "I need to keep up with the Joneses.",
        "When I have nice things, I have more self-esteem",
        "People with more money are more important than people with less money.",
        "Money makes your life more appealing."
    ],
    "Money Anxiety": "Believe that  if they do not have enough money, they should be fearful"
    [
        "Never pay for something you can do yourself.",
        "Money should be saved at all costs.",
        "I do not spend money when I don't have to pay.",
        "Paying for luxury is a waste.",
        "You should always keep as much money as possible for an emergency."
    ]
}

# Description for each category
descriptions = {
    "Money Resentment": "Money Resenters believe that money causes more problems in the world than it solves. This belief may be formed from some financial trauma in their past or family/social conditioning. They may believe that corporations control much of the world&#39;s economic power, and that ordinary people are exploited by capitalists. This manifests in behaviours that undermine their financial security. This could include giving away too much money, not investing, not educating themselves on financial products, never buying a house and not attempting to improve their earning capacity.that they do not deserve money. They may believe that wealthy people are greedy or corrupt. They often believe that there is virtue in living with less money.",
    "Financial Fantasists": "Financial Fantasists believe that money that money, and having more money, is the key to all life’s problems. Financial fantasists are never happy with what they have and always strive for more. If they have a problem, they look for something to buy or a service that may solve the issue. So, they will look for a coaching service instead of being introspective; they will think that they need a bigger house if someone they know has a bigger house. They are often jealous of people who have more money than they do and feel uncomfortable in their presence. Their dream is to be known for their wealth, and they would prefer their friends to have less money than they do..",
    "Money Prestige": "Money Status seekers believe that believes that displays of wealth equate to their social standing. They are concerned with external validation, that someone notices the new car they are driving, the bag they have, or the watch they are wearing. These displays often come at the expense of their financial well-being and usually result in large amounts of debt and the mental health problems associated with toxic debt.",
    "Money Anxiety": "The Money Anxious are always be fearful that they do not have enough money. They constantly worry about spending money on anything nice, struggle to treat themselves, and would prefer to buy second-hand items rather than invest in quality items that will last. This is usually the result of growing up in poverty. Even if they have money, they do not spend it. They are known as “tight” or “cheap.” They do not pay for professional services and often spend many hours and energy doing things themselves when they could afford to have someone else do it professionally."
}

# Collate scores
scores = {category: 0 for category in questions}

print("Rate each statement from 1 to 5:\n1 = Strongly Disagree, 5 = Strongly Agree\n")

# Get user input
for category, qs in questions.items():
    print(f"\n{category}")
    for q in qs:
        while True:
            try:
                answer = int(input(f"{q}\nYour answer (1-5): "))
                if 1 <= answer <= 5:
                    scores[category] += answer
                    break
                else:
                    print("Please enter a number from 1 to 5.")
            except ValueError:
                print("Invalid input. Please enter a number from 1 to 5.")

# Show final results
print("\n--- Your Results ---")
for cat, score in scores.items():
    print(f"{cat}: {score} points")

# Determine highest scoring category
top_category = max(scores, key=scores.get)

print(f"\n🏆 Dominant Money Belief: {top_category}")
print(descriptions[top_category])