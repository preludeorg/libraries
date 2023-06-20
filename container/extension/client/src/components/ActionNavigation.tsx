import {
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  ListSubheader,
  Paper,
} from '@mui/material';
import StartIcon from '@mui/icons-material/Start';
import RefreshIcon from '@mui/icons-material/Refresh';
import EngineeringIcon from '@mui/icons-material/Engineering';
import { Credentials } from '@theprelude/sdk';

export default function ActionNavigation({
  credentials,
  handleDeployProbe,
  refreshContainers,
  configureCredentials,
}: {
  credentials: Credentials | null;
  handleDeployProbe: () => void;
  refreshContainers: () => void;
  configureCredentials: () => void;
}) {
  return (
    <Paper>
      <nav aria-label="deploy refresh">
        <List subheader={<ListSubheader>Container Actions</ListSubheader>}>
          <ListItem disablePadding>
            <ListItemButton onClick={handleDeployProbe} disabled={!credentials}>
              <ListItemIcon>
                <StartIcon />
              </ListItemIcon>
              <ListItemText primary="Deploy Probes" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={refreshContainers}>
              <ListItemIcon>
                <RefreshIcon />
              </ListItemIcon>
              <ListItemText primary="Refresh" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={configureCredentials}>
              <ListItemIcon>
                <EngineeringIcon />
              </ListItemIcon>
              <ListItemText primary="Set Credentials" />
            </ListItemButton>
          </ListItem>
        </List>
      </nav>
    </Paper>
  );
}
