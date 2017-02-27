# encoding:utf-8
import re
import pickle
import collections

str=r'<a aria-label="Stargazers" class="muted-link tooltipped tooltipped-s mr-3" href="/hvy/chainer-wasserstein-gan/stargazers"><svg aria-hidden="true" class="octicon octicon-star" height="16" version="1.1" viewbox="0 0 14 16" width="14"><path d="M14 6l-4.9-.64L7 1 4.9 5.36 0 6l3.6 3.26L2.67 14 7 11.67 11.33 14l-.93-4.74z" fill-rule="evenodd"></path></svg>16</a>'
nums=re.findall('[0-9]+',str)
print(nums[-1])