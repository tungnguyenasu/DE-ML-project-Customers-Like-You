# Individual reflection

Tung Nguyen, Data Engineer and ML Engineer (individual project), DS 5020 mini-project "Customers Like You"

**What I did.** I worked alone, so I held both roles. As Data Engineer I built `build_matrix.py`. It
loads both yearly sheets and drops the week they share. It cleans the log with one logged rule per
step, and it subtracts cancelled units from the order they cancel instead of only deleting the
cancellation lines. It holds out the last two months as a leak-free test set and builds the sparse
customer x product matrix. As ML Engineer I chose Truncated SVD before fitting anything, then compared
it with PCA on the same matrix. I chose k, the purchase value and the scoring rule on a separate
validation period, evaluated once on the test purchases, and built the customer map, the memo and the
slides. The final model beats best sellers by 13.5 points and runs the whole nightly job in under a
second.

**What I learned.** The textbook difference between PCA and SVD barely showed on this data. The matrix
is 98% zeros, so the "average customer" that PCA removes is under 5% of it, and both methods found the
same components. My prediction that PCA's first component would contrast kinds of shops was wrong: in
both methods it measures how much a customer buys. The bigger lesson was about the scoring rule. The
cosine rule in the brief lost to best sellers, because scaling every product vector to the same
length throws away how popular it is. Using dot products kept that signal. A plain 1/0 "bought it" flag
also beat counting units. Finally, I learned how easily test data leaks into decisions: I first compared
scoring rules on the test purchases, which is why I added the validation split and chose everything there.

**What I would change.** I would write the success targets and build the validation split on day one,
before running any comparison on the test purchases. I would also give new customers and new products a
proper fallback, because the model cannot serve them today. And I would remove the one delivery charge
that slipped through the product-code rule.
