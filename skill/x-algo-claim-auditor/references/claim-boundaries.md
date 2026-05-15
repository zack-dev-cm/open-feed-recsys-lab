# Claim Boundaries

Use this reference when auditing claims about the X For You algorithm.

## Safe Claims

These can be supported when evidence exists in the public repo:

- Phoenix uses retrieval and ranking stages.
- Phoenix ranking uses a transformer with candidate isolation.
- Phoenix predicts multiple engagement actions.
- Home Mixer combines candidate sources, hydrators, filters, scorers, selectors, and side effects.
- Public source includes weighted scoring logic or parameter names for action weights.
- Public source includes filters such as blocked/muted author, muted keyword, age, seen/served, topic, subscription, and visibility filtering.
- Public source includes Grox content-understanding components such as safety, spam, reply ranking, post embedding, or banger screening.
- Public source includes ads blending or brand-safety modules.
- Running Phoenix requires the Git LFS artifact to be downloaded and extracted.

## Unsafe Or Overclaimed Claims

Flag these as `misleading`, `unsupported`, or `not_public_repo` unless public code directly proves them:

- Exact reach prediction for a draft post.
- Exact engagement multipliers such as "reply is 150x a like" without public parameter values.
- Premium, political, demographic, or account-class boosts.
- Shadowban diagnosis.
- A local clone that exactly reproduces a user's live For You feed.
- Claims that public source contains every production weight, threshold, config, model version, or internal service.
- Claims based on private account analytics, cookies, DMs, private feeds, or logged-in X pages.

## Preferred Wording

Say:

> The public repo supports a weaker statement: ranking combines model-predicted action probabilities using configurable weights. It does not publish enough production parameter values to prove the exact multiplier in this claim.

Avoid:

> This is how the live X algorithm ranks your post.

Say:

> The public repo includes source for this component and enough code to inspect the mechanism. It does not prove live production behavior for a specific account.
