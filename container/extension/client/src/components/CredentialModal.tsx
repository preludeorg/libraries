import { useState } from 'react';
import { Credentials } from '@theprelude/sdk';
import SaveIcon from '@mui/icons-material/Save';
import Backdrop from '@mui/material/Backdrop';
import { Box, Button, Modal, TextField, Typography } from '@mui/material';
import DockerCli from '../docker/cli';

const style = {
  position: 'absolute' as const,
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: 400,
  bgcolor: 'background.paper',
  border: '2px solid #000',
  boxShadow: 24,
  p: 4,
};

export function CredentialModal({
  docker,
  setCredentials,
  modal,
  setModal,
}: {
  docker: DockerCli;
  setCredentials: (credentials: Credentials | null) => void;
  modal: boolean;
  setModal: (modal: boolean) => void;
}) {
  const [account, setUsername] = useState('');
  const [token, setPassword] = useState('');

  const handleSave = () => {
    docker.setCredentials({ account, token });
    setCredentials({ account, token });
    setModal(false);
  };

  return (
    <Modal
      open={modal}
      onClose={() => setModal(false)}
      aria-labelledby="credential-modal-title"
      aria-describedby="credential-modal-description"
      closeAfterTransition
      slots={{ backdrop: Backdrop }}
      slotProps={{
        backdrop: {
          timeout: 500,
        },
      }}
    >
      <Box sx={style}>
        <Typography id="modal-modal-title" variant="h6" component="h2">
          Set Credentials
        </Typography>
        <br />
        <TextField
          id="account"
          label="Account"
          variant="outlined"
          value={account}
          onChange={(e) => setUsername(e.target.value)}
          fullWidth
        />
        <TextField
          id="token"
          label="Token"
          variant="outlined"
          value={token}
          onChange={(e) => setPassword(e.target.value)}
          fullWidth
        />
        <br /> <br />
        <Button
          variant="contained"
          onClick={handleSave}
          startIcon={<SaveIcon />}
        >
          Save
        </Button>
      </Box>
    </Modal>
  );
}
