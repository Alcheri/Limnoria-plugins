# DALnetID TODO

## Future Expansion

1. Add DALnet-specific identify helpers beyond NickServ.

   Keep this limited to closely related DALnet services or identify flows so the plugin stays focused.

2. Support limited service-status or auth workflow checks.

   This could cover small, explicit checks that help operators confirm whether an identify action is likely to succeed.

3. Keep new settings under `plugins.DALnetID.*`.

   Any future configuration should stay within the DALnetID namespace so the plugin remains coherent after the rename.
