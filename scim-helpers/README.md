# SCIM helpers
## For everything
Load the save in SCIM, then you can run the script in browser devtools.

In chrome you might need to type in `allow pasting` if you want to paste the script in.

Note: Always read, understand and verify scripts before running them in your browser.

## find-object-by-id.js
Enter an object ID from a crash log in the search string. Resulting array will have objects with the object ID and world coordinates in it for all matching objects that are in world-space.

## delete-asymmetric-factory-connections.js
An attempt at an automated fix for `Assertion failed: mConnectedComponent->IsConnected()` related crashes.

This will delete all conveyors and conveyor attachments that have asymmetrical connections. Remember to always back-up your saves before modifying them!

This is usually caused by blueprints which have a conveyor, splitter, merger, or other buildable that stays behind when a blueprint designer is cleared. A bug that occurs during placement of the buildable leads to the buildable not being attached to the blueprint designer, this buildable is now in world-space instead. This in turn leads to an FGFactoryConnectionComponent that is attached to a world-space ID'd object on one end being saved in the blueprint.

When a new copy of the blueprint is placed in-world, these kinds of connections are asymmetrical: The buildable in the placed blueprint connects to the one in the blueprint designer, but the buildable in the blueprint designer does not connect back to the newly placed blueprint. Alternatively, the blueprint is no longer in the designer, and the newly placed connection connects to nothing.

You might need to load this save by clearing all saves from your server save directory first. The crash in question can also occur when _unloading the previous save_, making loading saves through the server manager impossible.
