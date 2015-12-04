Version 0.0.12
--------------

Make the neighbor_name property required again (released on December 4 2015)

- Make neighbor_name required again for backward compatibility before BPSO-4421 is fixed

Version 0.0.11
--------------

Remove neighbor_name processing in BGP (released on December 3 2015)

- Remove BGP neighbor_name processing and make the property optional

Version 0.0.10
--------------

Support GET retries for POST command and update relationship definition (released on November 24 2015)

- Support GET retries for interface during a POST

- Update requirements and capabilities so it works with bpocore 1.2.1 validation 

Version 0.0.9
-------------

Fix typo in firewall definition (released on November 5 2015)

- Fix typo in firewall definition

Version 0.0.8
-------------

Move to Artifactory and more discovery strategy config (released on October 26 2015)

- Move to Artifactory and update dependencies

- Detailed configs for discovery strategy (specifically, enable immediateDelete and API specifics)

Version 0.0.7
-------------

Fix missing global router (released on October 13 2015)

### Bug Fixes
- Fix logic of global router so it will always exist even without protocol config

Version 0.0.6
-------------

Support Virtual Routers (released on September 29 2015)

-Support Virtual Routers (routing instances and global router)

Version 0.0.5
-------------

Support BGP configuration (released on August 31 2015)

-Support BGP configuration and discovery
-Bump rpsdk dependency to 0.2.9

Version 0.0.4
-------------

Use bpprov-full driver for interfaces (released on August 7 2015)

-Bump rpsdk dependency to 0.2.8
-use bpprov-full driver for interfaces to return orchState

Version 0.0.3
-------------

Use rpsdk 0.2.7 (released on August 5 2015)

-A typegroup issue when forming device resources is fixed as a result

Version 0.0.2
-------------

Onbarding enhancements (released on July 25 2015)

-Bump rpsdk dependency to 0.2.5
-Support UI schema onboarding and onboard retries

Version 0.0.1
-------------

Initial Juniper RA (released on July 23 2015)

-Converted from Juniper EA 2.0.0.dev1

