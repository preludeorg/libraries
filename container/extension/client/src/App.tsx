import { Box, Stack } from '@mui/material';
import { MouseEvent, useEffect, useState } from 'react';
import DockerCli from './docker/cli';
import { ActionAlert, DockerContainer, ProbeStatus } from './docker/types';
import ContainerTable from './components/ContainerTable';
import ActionNavigation from './components/ActionNavigation';
import { ActionStatus } from './components/ActionStatus';
import { Credentials } from '@theprelude/sdk';
import { CredentialModal } from './components/CredentialModal';

const docker = new DockerCli();

export function App() {
  const [selected, setSelected] = useState<readonly string[]>([]);
  const [containers, setContainers] = useState<DockerContainer[]>([]);
  const [refreshInterval] = useState(5 * 1000);
  const [alert, setAlert] = useState<ActionAlert | null>(null);
  const [credentials, setCredentials] = useState<Credentials | null>(
    docker.getCredentials(),
  );
  const [configCreds, setConfigCreds] = useState(false);

  const isSelected = (id: string) => selected.indexOf(id) !== -1;
  const handleClick = (event: MouseEvent<unknown>, name: string) => {
    const selectedIndex = selected.indexOf(name);
    let newSelected: readonly string[] = [];

    if (selectedIndex === -1) {
      newSelected = newSelected.concat(selected, name);
    } else if (selectedIndex === 0) {
      newSelected = newSelected.concat(selected.slice(1));
    } else if (selectedIndex === selected.length - 1) {
      newSelected = newSelected.concat(selected.slice(0, -1));
    } else if (selectedIndex > 0) {
      newSelected = newSelected.concat(
        selected.slice(0, selectedIndex),
        selected.slice(selectedIndex + 1),
      );
    }

    setSelected(newSelected);
  };

  const refreshContainers = () => {
    docker
      .listContainers()
      .then((containers: DockerContainer[]) => {
        docker
          .checkDependencies(containers)
          .then((updated: DockerContainer[]) => {
            setContainers(updated);
          })
          .catch((err) => {
            fireAlert('Dependency check failed', 'error', err.message);
            setContainers(containers);
          });
      })
      .catch((err) => {
        fireAlert('Failed to fetch containers', 'error', err.message);
        setContainers([]);
      });
  };

  const fireAlert = (title: string, level: string, message: string) => {
    setAlert({ title, level, message });
    setTimeout(() => {
      setAlert(null);
    }, 5000);
  };

  const handleDeployProbe = async () => {
    let valid = containers.filter((container) => isSelected(container.Id));
    if (!valid.length) {
      fireAlert('No containers selected', 'warning', 'Please select one');
      return;
    }
    valid = valid.filter(
      (container) => container.ProbeStatus !== ProbeStatus.Unsupported,
    );
    if (!valid.length) {
      fireAlert(
        'No supported containers selected',
        'warning',
        'Please select one',
      );
      return;
    }

    fireAlert('Deploying probes...', 'info', 'Please wait');
    const updates = await Promise.all(
      valid.map(async (container: DockerContainer) => {
        container.ProbeStatus = await docker.deployProbe(container.Id);
        return container;
      }),
    );

    const newContainers = containers.map((container) => {
      const update = updates.find((update) => update.Id === container.Id);
      return update || container;
    });

    setContainers(newContainers);
    refreshContainers();
  };

  const handleRefreshProbes = async () => {
    fireAlert('Refreshing data...', 'info', 'Please wait');
    refreshContainers();
  };

  useEffect(refreshContainers, []);
  useEffect(() => {
    if (refreshInterval && refreshInterval > 0) {
      const interval = setInterval(refreshContainers, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [refreshInterval]);

  return (
    <Box>
      <Stack direction="row" style={{ height: '83vh' }} spacing={2}>
        <div style={{ width: '20%' }}>
          <ActionNavigation
            credentials={credentials}
            handleDeployProbe={handleDeployProbe}
            refreshContainers={handleRefreshProbes}
            configureCredentials={() => setConfigCreds(true)}
          />
        </div>
        <div style={{ width: '80%' }}>
          <ContainerTable
            containers={containers}
            isSelected={isSelected}
            handleClick={handleClick}
          />
        </div>
      </Stack>
      {alert && (
        <ActionStatus
          title={alert.title}
          level={alert.level}
          message={alert.message}
        />
      )}
      <CredentialModal
        docker={docker}
        credentials={credentials}
        setCredentials={setCredentials}
        modal={configCreds}
        setModal={setConfigCreds}
      />
    </Box>
  );
}
