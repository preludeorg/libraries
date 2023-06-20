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

export default function ActionNavigation({
  handleDeployProbe,
  refreshContainers,
}: {
  handleDeployProbe: () => void;
  refreshContainers: () => void;
}) {
  return (
    <Paper>
      <nav aria-label="deploy refresh">
        <List subheader={<ListSubheader>Container Actions</ListSubheader>}>
          <ListItem disablePadding>
            <ListItemButton onClick={handleDeployProbe}>
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
        </List>
      </nav>
    </Paper>
  );
}
