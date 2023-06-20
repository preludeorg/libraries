import {
  Alert,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
} from '@mui/material';
import { MouseEvent, useState, useMemo } from 'react';
import { DockerContainer } from '../docker/types';
import Checkbox from '@mui/material/Checkbox';
import { ProbeStatusIcon } from './ProbeStatus';

export default function ContainerTable({
  containers,
  isSelected,
  handleClick,
}: {
  containers: DockerContainer[];
  isSelected: (id: string) => boolean;
  handleClick: (event: MouseEvent<unknown>, name: string) => void;
}) {
  const [page, setPage] = useState(0);
  const rowsPerPage = 10;
  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const visibleRows = useMemo(
    () =>
      containers
        .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
        .sort(),
    [containers, page, rowsPerPage],
  );

  return (
    <Paper>
      <TableContainer>
        <Table
          sx={{ minWidth: 750 }}
          aria-labelledby="tableTitle"
          size={'small'}
        >
          <TableHead>
            <TableRow key={'container-table-header'}>
              <TableCell padding="checkbox"></TableCell>
              <TableCell>Name</TableCell>
              <TableCell align={'center'}>Image</TableCell>
              <TableCell align={'center'}>Probe Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {visibleRows.length ? (
              visibleRows.map((container: DockerContainer, index: any) => {
                const isItemSelected = isSelected(container.Id);
                const labelId = `container-table-${index}`;
                return (
                  <TableRow
                    hover
                    onClick={(event) => handleClick(event, container.Id)}
                    role="checkbox"
                    aria-checked={isItemSelected}
                    tabIndex={-1}
                    key={container.Id}
                    selected={isItemSelected}
                    sx={{ cursor: 'pointer' }}
                  >
                    <TableCell padding="checkbox">
                      <Checkbox
                        color="primary"
                        checked={isItemSelected}
                        inputProps={{
                          'aria-labelledby': labelId,
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      {container.Names[0].replaceAll('/', '')}
                    </TableCell>
                    <TableCell align={'center'}>{container.Image}</TableCell>
                    <TableCell align={'center'}>
                      <ProbeStatusIcon status={container.ProbeStatus} />
                    </TableCell>
                  </TableRow>
                );
              })
            ) : (
              <TableRow key={'no-containers'}>
                <TableCell colSpan={4}>
                  <Alert severity="info" variant="outlined">
                    No running containers found
                  </Alert>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={[10]}
        component="div"
        count={containers.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
      />
    </Paper>
  );
}
