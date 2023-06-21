import { Alert, AlertTitle, AlertColor, Fade } from '@mui/material';
import { ActionAlert } from '../docker/types';

export function ActionStatus({ title, level, message }: ActionAlert) {
  return (
    <Fade in={true}>
      <Alert severity={level as AlertColor}>
        <AlertTitle>{title}</AlertTitle>
        {message}
      </Alert>
    </Fade>
  );
}
