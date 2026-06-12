# -*- coding: utf-8 -*-
"""Per-blog SHORT video scripts (v14 story arc), keyed by publish-tracker slug.
Arc: DID YOU KNOW? (real fact) -> HERE'S HOW (names the child + promise) ->
     STEP 1..N (the blog's concrete steps) -> THE CRUX (the blog's core lesson).
Each entry: {script, palette, final_slug, title}. caption_for(slug) = SEO IG-Reel caption."""


def _s(did_know, did_accent, promise, promise_accent, steps, crux, crux_accent, cta_tag, cta_accent=None):
    """steps = list of (text, accent). cta_tag = theme-specific closing line (URL bar added by the engine).
    Builds the scene-script dict consumed by video_engine."""
    return dict(
        did_know=did_know, did_accent=did_accent,
        promise=promise, promise_accent=promise_accent,
        steps=[("STEP %d" % (i + 1), t, a) for i, (t, a) in enumerate(steps)],
        crux=crux, crux_accent=crux_accent,
        cta_tag=cta_tag, cta_accent=cta_accent, cta_url="habbinson.com/blog",
        cta_line=crux,                       # back-compat (YouTube desc + caption fallback)
    )


SCRIPTS = {
 "how-to-praise-your-child": dict(palette="sunny", final_slug="how-to-praise-your-child",
   title="How to Praise Your Child the Right Way",
   script=_s("Po had ZERO talent in Kung Fu Panda", "ZERO",
             "Want a brave, confident child? Do this:", "CONFIDENT",
             [("Praise the effort, not the word smart", "EFFORT"),
              ("Say exactly what they did well", None),
              ("Make mistakes safe to make", "SAFE")],
             "Praise the effort, and your child keeps trying when things get hard.", "EFFORT",
             "Want to raise a confident, resilient child? Read the full step-by-step guide", "CONFIDENT")),
 "why-calm-down-doesnt-work": dict(palette="coral", final_slug="how-to-calm-an-angry-child",
   title="How to Calm an Angry Child the Right Way",
   script=_s("In Inside Out, Joy couldn't fix sadness", "SADNESS",
             "Want to calm an angry child? Do this:", "ANGRY",
             [("Get calm yourself first", "CALM"),
              ("Name the feeling out loud", None),
              ("Connect before you correct", "CONNECT")],
             "Big feelings settle when a child feels seen, not silenced.", "SEEN",
             "Want to raise a calm, emotionally strong child? Read the full guide", "CALM")),
 "how-to-get-kids-to-cooperate-choices": dict(palette="sky", final_slug="how-to-get-kids-to-cooperate",
   title="How to Get Kids to Cooperate",
   script=_s("Dumbledore said our CHOICES define us", "CHOICES",
             "Want your child to cooperate? Do this:", "COOPERATE",
             [("Offer two options you're happy with", "TWO"),
              ("Let them pick one", None),
              ("Keep the rule, share the control", "CONTROL")],
             "A real choice ends the power struggle, and the rule still stands.", "CHOICE",
             "Want to raise a cooperative child without the yelling? Read the full guide", "COOPERATIVE")),
 "how-to-get-your-child-to-open-up": dict(palette="mint", final_slug="how-to-get-your-child-to-open-up",
   title="How to Get Your Child to Open Up",
   script=_s("In Dangal, trust was built side by SIDE", "SIDE",
             "Want a quiet child to open up? Do this:", "OPEN",
             [("Sit beside them, not across", "BESIDE"),
              ("Talk in the car or at bedtime", None),
              ("Listen first, fix later", "LISTEN")],
             "Kids open up sideways, through time together, not questions.", "TOGETHER",
             "Want to raise a child who opens up to you? Read the full guide", "OPENS")),
 "help-your-child-speak-with-confidence": dict(palette="grape", final_slug="help-your-child-speak-with-confidence",
   title="Help Your Child Speak With Confidence",
   script=_s("The King beat his stammer with a PAUSE", "PAUSE",
             "Want your child to sound confident? Do this:", "CONFIDENT",
             [("Teach one slow breath before talking", "BREATH"),
              ("Pause two seconds, then speak", None),
              ("Praise the calm, not just the words", "CALM")],
             "Confidence is calm you can practice, one pause at a time.", "CALM",
             "Want to raise a confident speaker? Read the full step-by-step guide", "CONFIDENT")),
 "stop-rescuing-your-child": dict(palette="lime", final_slug="stop-rescuing-your-child",
   title="Stop Rescuing Your Child",
   script=_s("In Finding Nemo, overprotection backfired", "NEMO",
             "Want a child with real grit? Do this:", "GRIT",
             [("Let small, safe struggles happen", "STRUGGLES"),
              ("Coach them, don't fix it for them", None),
              ("Let consequences do the teaching", "TEACH")],
             "Every struggle you don't rescue becomes your child's strength.", "STRENGTH",
             "Want to raise a child with real grit? Read the full step-by-step guide", "GRIT")),
 "ask-your-child-whats-your-plan": dict(palette="sunny", final_slug="build-problem-solving-skills-in-kids",
   title="How to Build Problem-Solving Skills in Kids",
   script=_s("In 3 Idiots, Rancho asked WHY, not what", "WHY",
             "Want a child who thinks for themselves? Do this:", "THINKS",
             [("Stop handing over the answer", "STOP"),
              ("Ask them: what's your plan?", "PLAN"),
              ("Let them try it, even if it's wrong", None)],
             "Ask, don't answer, and a real problem-solver grows.", "ASK",
             "Want to raise a child who thinks for themselves? Read the full guide", "THINKS")),
 "what-to-do-after-you-yell-at-your-child": dict(palette="coral", final_slug="what-to-do-after-you-yell-at-your-child",
   title="What to Do After You Yell at Your Child",
   script=_s("Mufasa got angry, then made it right", "RIGHT",
             "Just yelled at your child? Do this next:", "NEXT",
             [("Get calm, then go back", "CALM"),
              ("Say sorry for the yelling", None),
              ("Keep the limit, restore the love", "LOVE")],
             "Repair beats perfect, and that's how trust survives a bad moment.", "REPAIR",
             "Want to raise a child who trusts you? Read the full step-by-step guide", "TRUSTS")),
 "let-your-child-fail-on-purpose": dict(palette="sky", final_slug="let-your-child-fail-on-purpose",
   title="Let Your Child Fail on Purpose",
   script=_s("Michael Jordan was CUT from his team", "CUT",
             "Want a resilient child? Do this:", "RESILIENT",
             [("Allow small, safe flops", "FLOPS"),
              ("Skip the lecture, coach the comeback", None),
              ("Treat failure as information", "FAILURE")],
             "Failure isn't the end, it's the data your child grows from.", "GROWS",
             "Want to raise a resilient child? Read the full step-by-step guide", "RESILIENT")),
 "give-your-child-5-dollars-and-a-challenge": dict(palette="mint", final_slug="raise-an-entrepreneurial-child",
   title="How to Raise an Entrepreneurial Child",
   script=_s("Warren Buffett sold gum door to door as a KID", "KID",
             "Want your child to be an entrepreneur? Do this:", "ENTREPRENEUR",
             [("Give them $5 and one goal: grow it", "$5"),
              ("Let them plan, sell, and even fail", None),
              ("Let them keep what they earn", "KEEP")],
             "Real money plus real ownership builds a child who thinks like a founder.", "FOUNDER",
             "Want to raise a young entrepreneur? Read the full step-by-step guide", "ENTREPRENEUR")),
}


# ---- SEO-dense IG Reel captions: keyword-rich lines + save/share/follow CTA + 12-15 hashtags + signature ----
_CTA = ("\n\n\U0001F4BE Save this and send it to a parent who needs it."
        "\n\U0001F449 Follow @adnanbuildsleaders for daily parenting, communication & leadership tips.")
_SIG = "\n\nDon't just raise a child — raise a leader."


def _rc(lead, value, tags):
    return lead + "\n\n" + value + _CTA + "\n\n" + " ".join("#" + t for t in tags) + _SIG


REEL_CAPTIONS = {
 "how-to-praise-your-child": _rc(
   "Did you know Po had ZERO talent in Kung Fu Panda? Stop calling your child “smart.”",
   "Praising the label kills effort. Praise the effort and the exact thing they did well, and you raise a brave kid who keeps trying. This is how to praise your child the right way and build real confidence.",
   ["parenting","parentingtips","raisingleaders","positiveparenting","confidentkids","growthmindset","childpsychology","gentleparenting","praise","kidsconfidence","momlife","dadlife","parenting101","raisealeader"]),
 "why-calm-down-doesnt-work": _rc(
   "Even Joy couldn't fix sadness in Inside Out. “Calm down” never works on an angry child.",
   "Big feelings don't switch off on command. Get calm yourself, name the feeling out loud, and connect before you correct. That's how to calm an angry child and teach real emotional control.",
   ["parenting","parentingtips","raisingleaders","emotionalintelligence","angrychild","gentleparenting","bigfeelings","childpsychology","tantrums","calmparenting","momlife","dadlife","emotionalregulation","raisealeader"]),
 "how-to-get-kids-to-cooperate-choices": _rc(
   "Dumbledore said our choices define us. Want your child to cooperate? Give two choices, not orders.",
   "Power struggles end when kids feel some control. Offer two options you're happy with, let them pick, and keep the rule while you share the control. That's how to get kids to cooperate without yelling.",
   ["parenting","parentingtips","raisingleaders","positiveparenting","toddlerlife","cooperation","gentleparenting","childpsychology","parentinghacks","powerstruggles","momlife","dadlife","parenting101","raisealeader"]),
 "how-to-get-your-child-to-open-up": _rc(
   "In Dangal, trust was built side by side. Want your quiet child to open up?",
   "Kids talk more side by side than face to face. Sit beside them, talk in the car or at bedtime, and listen first before you fix. That's how to get your child to open up and really communicate.",
   ["parenting","parentingtips","raisingleaders","communicationskills","quietchild","gentleparenting","connection","childpsychology","parentingteens","activelistening","momlife","dadlife","parentchild","raisealeader"]),
 "help-your-child-speak-with-confidence": _rc(
   "The King beat his stammer with one pause. Help your child sound confident the same way.",
   "Confidence is a skill, not a gift. Teach one slow breath before speaking, pause two seconds, then talk — and praise the calm, not just the words. That's how to help your child speak with confidence.",
   ["parenting","parentingtips","raisingleaders","confidentkids","publicspeaking","communicationskills","selfconfidence","childpsychology","shykids","speakup","momlife","dadlife","leadershipskills","raisealeader"]),
 "stop-rescuing-your-child": _rc(
   "In Finding Nemo, overprotection backfired. Stop rescuing your child — you're stealing the lesson.",
   "Saving kids from every struggle builds anxiety, not safety. Let small safe struggles happen, coach instead of fixing, and let consequences teach. That's how to build resilience and grit in your child.",
   ["parenting","parentingtips","raisingleaders","resilience","grit","gentleparenting","overparenting","childpsychology","independence","raisingboys","momlife","dadlife","parenting101","raisealeader"]),
 "ask-your-child-whats-your-plan": _rc(
   "In 3 Idiots, Rancho asked WHY, not what. One question builds a problem-solver: “What's your plan?”",
   "Stop handing kids the answer. Ask “what's your plan?” and let them try it, even if it's wrong. That's how to build problem-solving skills and raise a child who thinks for themselves.",
   ["parenting","parentingtips","raisingleaders","problemsolving","criticalthinking","growthmindset","childpsychology","independence","raisingthinkers","parentinghacks","momlife","dadlife","leadershipskills","raisealeader"]),
 "what-to-do-after-you-yell-at-your-child": _rc(
   "Even Mufasa got angry, then made it right. Yelled at your child? Here's how to repair it.",
   "Every parent loses it sometimes. Get calm, go back, say sorry for the yelling, then keep the limit and restore the love. That's what to do after you yell at your child — and how trust survives.",
   ["parenting","parentingtips","raisingleaders","gentleparenting","repair","mindfulparenting","childpsychology","yelling","emotionalintelligence","parentingsupport","momlife","dadlife","parentchild","raisealeader"]),
 "let-your-child-fail-on-purpose": _rc(
   "Michael Jordan was CUT from his team. Let your child fail on purpose — it's how leaders are made.",
   "Failure is information, not the end. Allow small safe flops, skip the lecture, and coach the comeback. That's how to build resilience and raise a child who isn't afraid to try hard things.",
   ["parenting","parentingtips","raisingleaders","resilience","failforward","growthmindset","grit","childpsychology","mentalstrength","raisingboys","momlife","dadlife","leadershipskills","raisealeader"]),
 "give-your-child-5-dollars-and-a-challenge": _rc(
   "Warren Buffett sold gum door to door as a kid. Give your child $5 and one challenge.",
   "Entrepreneurial kids learn by doing. Give them $5 and one goal: grow it. Let them plan, sell, even fail — and keep what they earn. That's how to raise an entrepreneurial child with real money skills.",
   ["parenting","parentingtips","raisingleaders","entrepreneurkids","moneyskills","financialliteracy","growthmindset","childpsychology","entrepreneurship","raisingleaders","momlife","dadlife","leadershipskills","raisealeader"]),
}



# ---- June-8 famous-person blogs: register so the cloud IG poster recognizes them ----
# (videos are pre-built in assets/<slug>.mp4; YouTube Shorts pre-scheduled via publishAt.)
_JUN08_META = {
  'late-talking-child': ('sky', 'Late Talking Child? The Lesson Hidden in Einstein'),
  'your-restless-child-is-gifted': ('lime', 'Restless Child? The Hidden Gift Sachin Almost Lost'),
  'help-a-child-who-stammers': ('coral', 'Child Who Stammers? The Hrithik Roshan Lesson'),
  'dyslexia-is-not-a-weakness': ('sunny', "Dyslexia in Children: Why a 'Weak' Student Can Win Big"),
  'encourage-curiosity-in-kids': ('grape', "Curiosity in Children: Stop Saying 'Because I Said So'"),
  'why-boredom-is-good-for-kids': ('mint', 'Why Boredom Is Good for Kids (And Builds Creativity)'),
  'raise-an-opportunity-spotter': ('sky', 'Raise an Entrepreneur: Teach Your Child to Spot Opportunity'),
  'public-speaking-for-kids': ('grape', 'Public Speaking for Kids: Raise a Child Who Holds the Room'),
  'raise-a-child-who-loves-reading': ('sky', 'Raise a Child Who Loves Reading (Like Bill Gates)'),
  'believe-in-your-child': ('coral', "Believe in Your Child When the World Says 'Too Small'"),
}
for _jslug, (_jpal, _jtitle) in _JUN08_META.items():
    SCRIPTS[_jslug] = dict(palette=_jpal, final_slug=_jslug, title=_jtitle)

REEL_CAPTIONS.update({
  'late-talking-child': "Is your child a late talker? Einstein spoke late too. Here's how to help a late talking child start speaking — 3 simple, science-backed steps any parent can use at home today. Follow @adnanbuildsleaders for daily parenting + communication tips. Save & share this with a parent who needs it. #latetalker #toddlertalk #speechdelay #parentingtips #raisealeader #adnanbuildsleaders #toddlermilestones #kidscommunication #parentinghacks #earlychildhood\n\nDon't just raise a child — raise a leader.",
  'your-restless-child-is-gifted': "Got a restless, high-energy child who can't sit still? It might be their biggest gift. Sachin Tendulkar was a restless kid too — here's how to channel that energy into focus and confidence. Follow @adnanbuildsleaders for daily parenting + communication tips. Save & share with a tired parent! #restlesschild #highenergykids #parentingtips #raisealeader #adnanbuildsleaders #activekids #channeltheenergy #toddlerlife #parentinghacks #sachintendulkar\n\nDon't just raise a child — raise a leader.",
  'help-a-child-who-stammers': "Worried about a child who stammers or stutters? Hrithik Roshan stammered as a kid too. Here's what really helps a stuttering child speak with confidence — and the well-meaning mistakes to avoid. Follow @adnanbuildsleaders for daily parenting + communication tips. Save & share! #childwhostammers #stuttering #speechtherapy #parentingtips #raisealeader #adnanbuildsleaders #kidsconfidence #communicationskills #hrithikroshan #speechconfidence\n\nDon't just raise a child — raise a leader.",
  'dyslexia-is-not-a-weakness': "Does your child struggle with reading? Dyslexia in children is NOT low intelligence — Richard Branson is dyslexic and built an empire. Here's how to turn a struggling reader's brain into a strength. Follow @adnanbuildsleaders for daily parenting + communication tips. Save & share! #dyslexia #strugglingreader #dyslexicthinking #parentingtips #raisealeader #adnanbuildsleaders #learningdifferences #raiseanentrepreneur #richardbranson #neurodiversity\n\nDon't just raise a child — raise a leader.",
  'encourage-curiosity-in-kids': "Tired of your child's endless 'why' questions? That curiosity is a superpower. Leonardo da Vinci never stopped asking why — here's how to feed your child's curiosity instead of shutting it down. Follow @adnanbuildsleaders for daily parenting + communication tips. Save & share! #curiouskids #curiosity #raisealeader #parentingtips #adnanbuildsleaders #kidslearning #askwhy #davinci #raiseathinker #earlylearning\n\nDon't just raise a child — raise a leader.",
  'why-boredom-is-good-for-kids': "Should you let your child be bored? YES. J.K. Rowling dreamed up Harry Potter bored on a train. Here's why boredom is good for kids and builds creativity — and what to do instead of grabbing a screen. Follow @adnanbuildsleaders for daily parenting + communication tips. Save & share! #boredom #boredkids #creativity #parentingtips #raisealeader #adnanbuildsleaders #screenfree #letthemplay #jkrowling #imaginativeplay\n\nDon't just raise a child — raise a leader.",
  'raise-an-opportunity-spotter': "Want to raise an entrepreneur? Dhirubhai Ambani started with almost nothing and built an empire. Here's how to teach your child to spot opportunity and create value — starting young. Follow @adnanbuildsleaders for daily parenting + communication tips. Save & share! #raiseanentrepreneur #entrepreneurkids #moneyskills #parentingtips #raisealeader #adnanbuildsleaders #futureskills #kidsbusiness #dhirubhaiambani #opportunity\n\nDon't just raise a child — raise a leader.",
  'public-speaking-for-kids': "Got a bright child who won't speak up? Public speaking for kids is a learnable skill. Oprah was speaking to audiences by age 3 — here's how to raise a child who can hold a room. Follow @adnanbuildsleaders for daily parenting + communication tips. Save & share! #publicspeaking #confidentkids #communicationskills #parentingtips #raisealeader #adnanbuildsleaders #shychild #kidsconfidence #oprah #speakup\n\nDon't just raise a child — raise a leader.",
  'raise-a-child-who-loves-reading': "Want to raise a child who loves reading in a world of screens? Bill Gates devoured books as a kid. Here's how to grow a reader — and why early reading shapes the brain. Follow @adnanbuildsleaders for daily parenting + communication tips. Save & share! #raiseareader #kidsreading #readinghabit #parentingtips #raisealeader #adnanbuildsleaders #readaloud #earlyliteracy #billgates #booksforkids\n\nDon't just raise a child — raise a leader.",
  'believe-in-your-child': "When the world says your child is 'too small' or 'not enough,' believe in them anyway. Messi was told he was too small. Here's how to build unshakeable self-belief in kids. Follow @adnanbuildsleaders for daily parenting + communication tips. Save & share! #believeinyourchild #selfbelief #confidentkids #resilience #parentingtips #raisealeader #adnanbuildsleaders #growthmindset #messi #neverquit\n\nDon't just raise a child — raise a leader.",
})


def caption_for(slug):
    """SEO reel caption for a blog slug; falls back to a generic branded caption."""
    if slug in REEL_CAPTIONS:
        return REEL_CAPTIONS[slug]
    m = SCRIPTS.get(slug, {})
    lead = (m.get("script", {}).get("cta_line") or "New on the blog.")
    return _rc(lead, "Read the full guide on habbinson.com/blog.",
               ["parenting","parentingtips","raisingleaders","childpsychology","positiveparenting",
                "communicationskills","confidentkids","gentleparenting","momlife","dadlife","raisealeader"])
