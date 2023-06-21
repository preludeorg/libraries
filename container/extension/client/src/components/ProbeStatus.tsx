import { ProbeStatus } from '../docker/types';
import { Tooltip } from '@mui/material';
import DirectionsRunIcon from '@mui/icons-material/DirectionsRun';
import CloseIcon from '@mui/icons-material/Close';
import { pink } from '@mui/material/colors';
import DoDisturbIcon from '@mui/icons-material/DoDisturb';

export function ProbeStatusIcon({ status }: { status: ProbeStatus }) {
  switch (status) {
    case ProbeStatus.Running:
      return (
        <Tooltip title="Running">
          <DirectionsRunIcon color="success" />
        </Tooltip>
      );
    case ProbeStatus.NotInstalled:
      return (
        <Tooltip title="Not installed">
          <CloseIcon sx={{ color: pink[500] }} />
        </Tooltip>
      );
    default:
      return (
        <Tooltip title="Unsupported">
          <DoDisturbIcon color="disabled" />
        </Tooltip>
      );
  }
}
