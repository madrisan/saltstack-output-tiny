[![License](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](https://spdx.org/licenses/Apache-2.0.html)

![](images/saltstack_horizontal_dark.png?raw=true)

# SaltStack output module "tiny"

A Salt _outputter_ module is a Python module placed in a directory called `_output/` at the root of the Salt fileserver, usually `/srv/salt`. Outputter modules display affect how that data is shown to the user.

The _tiny_ outputter displays the results of state runs the most succint way, and can be selected by using the command-line option _--out_:

```bash
   salt-ssh <minion-id> state.apply <state> --out tiny
```


